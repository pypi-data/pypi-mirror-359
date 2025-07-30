# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import resample
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.pipeline import Pipeline
from feature_engine.selection import MRMR # Leveraging feature_engine for core mRMR filter
import copy

class RobustMRMRSelector(BaseEstimator, TransformerMixin):
    """
    A robust feature selection transformer that combines ensemble Minimum Redundancy
    Maximum Relevance (mRMR) with an optional refinement step, designed for
    seamless integration into scikit-learn pipelines and hyperparameter optimization.

    This selector first performs multiple mRMR runs on bootstrapped samples of the
    data (ensemble mRMR) to generate robust feature importance scores (based on vote
    count). It then selects a preliminary set of features based on these scores.
    Optionally, a `refiner_estimator` (e.g., RFE, SelectFromModel) can be applied
    to this preliminary set for further, model-specific feature selection.

    Parameters
    ----------
    n_features_to_select : int, optional (default=10)
        The final number of features to select. This is the primary parameter
        to be tuned via GridSearchCV or RandomizedSearchCV.
    n_ensembles : int, optional (default=5)
        The number of ensemble (bootstrapped) mRMR runs to perform. Higher values
        increase robustness but also computation time.
    subsample_ratio : float, optional (default=1.0)
        The proportion of samples to use for each ensemble run. If 1.0,
        bootstrapping (sampling with replacement) is used. If < 1.0,
        subsampling (sampling without replacement) is used.
        Must be between 0 and 1.
    mrmr_scheme : {'MID', 'MIQ'}, optional (default='MID')
        The mRMR scheme to use for the internal `feature_engine.selection.MRMR` runs:
        'MID' (Mutual Information Difference): Max(MI(f,y) - 1/|S| * sum(MI(f,fj)))
        'MIQ' (Mutual Information Quotient): Max(MI(f,y) / (1/|S| * sum(MI(f,fj))))
    refiner_estimator : estimator, optional (default=None)
        An optional scikit-learn compatible estimator (e.g., `RFE`, `SelectFromModel`,
        `SequentialFeatureSelector`) to further refine the features selected by
        the ensemble mRMR. This estimator will operate on the features
        selected by the ensemble mRMR. If None, only ensemble mRMR is used.
        Note: If `refiner_estimator` has `n_features_to_select`, it will be
        set to the `n_features_to_select` of this class.
        If the `refiner_estimator` requires preprocessing (e.g., scaling), it is
        recommended to wrap it in a `sklearn.pipeline.Pipeline` before passing it
        to `RobustMRMRSelector`.
    classification : bool, optional (default=True)
        True if the problem is a classification task (uses mutual_info_classif for MI
        calculation). False for regression tasks (uses mutual_info_regression).
    random_state : int, optional (default=42)
        Controls the randomness of bootstrapping for reproducibility.

    Attributes
    ----------
    selected_features_ : list
        List of selected feature names after fitting.
    feature_importances_ : dict
        Dictionary of raw importance scores (vote counts) for each feature
        from the ensemble mRMR process.
    _original_columns : list
        Stores the column names of the input DataFrame during fit.
    """

    def __init__(self, n_features_to_select=10, n_ensembles=5, subsample_ratio=1.0,
                 mrmr_scheme='MID', refiner_estimator=None, classification=True,
                 random_state=42):
        self.n_features_to_select = n_features_to_select
        self.n_ensembles = n_ensembles
        self.subsample_ratio = subsample_ratio
        self.mrmr_scheme = mrmr_scheme
        self.refiner_estimator = refiner_estimator
        self.classification = classification
        self.random_state = random_state

        # Attributes to be set during fit
        self.feature_scores_ = None
        self.selected_features_ = None
        self._original_columns = None

        # Validate inputs
        if not isinstance(self.n_features_to_select, int) or self.n_features_to_select <= 0:
            raise ValueError("n_features_to_select must be a positive integer.")
        if not isinstance(self.n_ensembles, int) or self.n_ensembles <= 0:
            raise ValueError("n_ensembles must be a positive integer.")
        if not (0.0 < self.subsample_ratio <= 1.0):
            raise ValueError("subsample_ratio must be between 0 (exclusive) and 1 (inclusive).")
        if self.mrmr_scheme not in ['MID', 'MIQ']:
            raise ValueError("mrmr_scheme must be 'MID' or 'MIQ'.")
        if not isinstance(self.classification, bool):
            raise ValueError("classification must be a boolean.")

    def _run_single_mrmr_filter(self, X_sample, y_sample):
        """
        Runs a single mRMR selection using feature_engine.selection.MRMR.
        """
        # feature_engine.MRMR handles MI calculation internally based on problem type.
        # We need to pass the 'regression' parameter correctly.
        mrmr_internal = MRMR(
            method=self.mrmr_scheme,
            regression=not self.classification, # True if regression, False if classification
            cv=None # No internal CV needed for this filter step
        )
        mrmr_internal.fit(X_sample, y_sample)

        # feature_engine's MRMR returns 'features_to_drop_', so selected are the complement
        selected_in_run = list(X_sample.columns.difference(mrmr_internal.features_to_drop_))
        return selected_in_run

    def fit(self, X, y):
        """
        Fits the RobustMRMRSelector by performing ensemble mRMR and an optional
        refinement step.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data. Must be a pandas DataFrame or numpy array.
        y : array-like of shape (n_samples,)
            Target values. Must be a pandas Series or numpy array.

        Returns
        -------
        self : object
            Returns the instance itself.
        """
        # Input validation and conversion to DataFrame
        if not isinstance(X, (pd.DataFrame, np.ndarray)):
            raise TypeError("Input X must be a pandas DataFrame or numpy array.")
        if isinstance(X, np.ndarray):
            self._original_columns = [f"feature_{i}" for i in range(X.shape[1])]
            X_df = pd.DataFrame(X, columns=self._original_columns)
        else:
            self._original_columns = X.columns.tolist()
            X_df = X.copy() # Work on a copy to avoid modifying original

        if not isinstance(y, (pd.Series, np.ndarray)):
            raise TypeError("Input y must be a pandas Series or numpy array.")
        if isinstance(y, np.ndarray):
            y_series = pd.Series(y)
        else:
            y_series = y.copy() # Work on a copy

        if X_df.shape[1] < self.n_features_to_select:
            raise ValueError(
                f"n_features_to_select ({self.n_features_to_select}) cannot be "
                f"greater than the number of features in X ({X_df.shape[1]})."
            )

        # 1. Ensemble mRMR phase
        ensemble_feature_votes = {col: 0 for col in X_df.columns}

        # Determine number of features for individual ensemble runs.
        # This should be at least `n_features_to_select` or a reasonable fraction of total features.
        # We select a larger pool in each ensemble run to allow for robust voting.
        # The `initial_features_per_ensemble` is no longer passed to _run_single_mrmr_filter
        # as feature_engine.MRMR does not take this parameter in its constructor.
        # It will still be used to determine the preliminary features for refinement.
        initial_features_per_ensemble = min(max(self.n_features_to_select * 2, 20), X_df.shape[1])

        for i in range(self.n_ensembles):
            # Bootstrapping (with replacement) or subsampling (without replacement)
            # Use a different random state for each ensemble run
            current_random_state = self.random_state + i if self.random_state is not None else None

            if self.subsample_ratio == 1.0:
                # Bootstrapping (sampling with replacement)
                X_sample, y_sample = resample(X_df, y_series,
                                              stratify=y_series if self.classification else None,
                                              random_state=current_random_state)
            else:
                # Subsampling (sampling without replacement)
                n_samples_for_ensemble = int(len(X_df) * self.subsample_ratio)
                if n_samples_for_ensemble == 0:
                    raise ValueError("Subsample ratio is too small, resulting in 0 samples.")

                # Use train_test_split to get a subsample without replacement
                from sklearn.model_selection import train_test_split
                X_sample, _, y_sample, _ = train_test_split(
                    X_df, y_series, train_size=n_samples_for_ensemble,
                    stratify=y_series if self.classification else None,
                    random_state=current_random_state
                )

            selected_in_run = self._run_single_mrmr_filter(X_sample, y_sample)

            for feature_name in selected_in_run:
                ensemble_feature_votes[feature_name] = ensemble_feature_votes.get(feature_name, 0) + 1

        self.feature_scores_ = ensemble_feature_votes

        # Sort features by ensemble votes (most frequently selected first)
        sorted_features_by_vote = sorted(ensemble_feature_votes.items(), key=lambda item: item[1], reverse=True)
        ensemble_selected_features_names = [feat for feat, _ in sorted_features_by_vote]

        # Take a preliminary set of features for refinement (or final selection if no refiner)
        # This ensures the refiner has enough features to work with, even if n_features_to_select is small.
        preliminary_features_for_refinement = ensemble_selected_features_names[:max(self.n_features_to_select, initial_features_per_ensemble)]
        X_preliminary = X_df[preliminary_features_for_refinement]

        # 2. Refinement phase (if refiner_estimator is provided)
        if self.refiner_estimator is not None:
            # Create a deep copy of the refiner estimator to avoid modifying the original
            refiner = copy.deepcopy(self.refiner_estimator)

            # Set n_features_to_select for the refiner if it supports it and is not already set
            if hasattr(refiner, 'n_features_to_select') and getattr(refiner, 'n_features_to_select', None) is None:
                refiner.n_features_to_select = self.n_features_to_select
            elif hasattr(refiner, 'k') and getattr(refiner, 'k', None) is None: # For SelectKBest
                 refiner.k = self.n_features_to_select
            elif hasattr(refiner, 'threshold') and getattr(refiner, 'threshold', None) is None:
                # For SelectFromModel, converting n_features_to_select to a threshold is complex.
                # It's better for the user to set the threshold directly in refiner_estimator
                # or for us to provide a simple heuristic like 'median' or 'mean' if n_features_to_select is None.
                # For now, we assume user sets threshold or refiner handles n_features_to_select.
                pass

            # The user is responsible for wrapping the refiner in a Pipeline if preprocessing
            # (e.g., scaling) is required for the refiner.
            refiner_pipeline = refiner # Assume refiner can be a Pipeline directly

            refiner_pipeline.fit(X_preliminary, y_series)

            # Extract selected features from the refiner
            if hasattr(refiner_pipeline, 'get_support'):
                selected_indices_in_preliminary = refiner_pipeline.get_support(indices=True)
                self.selected_features_ = [preliminary_features_for_refinement[i] for i in selected_indices_in_preliminary]
            elif hasattr(refiner_pipeline, 'coef_') or \
                 hasattr(refiner_pipeline, 'feature_importances_'):

                importance_scores = getattr(refiner_pipeline, 'feature_importances_', None)
                if importance_scores is None:
                    importance_scores = getattr(refiner_pipeline, 'coef_', None)
                    if importance_scores is not None and importance_scores.ndim > 1: # Handle multi-output classifiers
                        importance_scores = np.linalg.norm(importance_scores, axis=0) # L2 norm for multi-output

                if importance_scores is not None:
                    feature_importances_dict = dict(zip(preliminary_features_for_refinement, importance_scores))
                    # If the refiner provides importance scores but not get_support, we sort by importance
                    # and then take self.n_features_to_select. This is the case where the refiner doesn't
                    # explicitly select a number, so we fall back to the overall desired number.
                    sorted_by_importance = sorted(feature_importances_dict.items(), key=lambda item: abs(item[1]), reverse=True)
                    self.selected_features_ = [feat for feat, _ in sorted_by_importance[:self.n_features_to_select]]
                else:
                    print("Warning: Refiner estimator does not provide 'get_support', 'coef_', or 'feature_importances_'. Falling back to top N from ensemble mRMR.")
                    self.selected_features_ = ensemble_selected_features_names[:self.n_features_to_select]
            else:
                print("Warning: Refiner estimator does not have 'get_support', 'coef_', or 'feature_importances_'. Falling back to top N from ensemble mRMR.")
                self.selected_features_ = ensemble_selected_features_names[:self.n_features_to_select]

            # The refiner's selection is the final selection. We do not truncate or modify it here.
            # The refiner itself is responsible for selecting the desired number of features.

        else:
            # If no refiner, just take top N from ensemble mRMR
            self.selected_features_ = ensemble_selected_features_names[:self.n_features_to_select]

        return self

    def transform(self, X):
        """
        Transforms the input data by selecting the features determined during fitting.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data to transform. Must be a pandas DataFrame or numpy array.

        Returns
        -------
        X_transformed : array-like of shape (n_samples, n_selected_features)
            Transformed data with only the selected features. Returns a DataFrame
            if input was DataFrame, else a NumPy array.
        """
        if self.selected_features_ is None:
            raise RuntimeError("RobustMRMRSelector not fitted yet. Call fit() first.")

        is_dataframe_input = isinstance(X, pd.DataFrame)

        if not isinstance(X, (pd.DataFrame, np.ndarray)):
            raise TypeError("Input X must be a pandas DataFrame or numpy array.")

        if isinstance(X, np.ndarray):
            # If original input was DataFrame, use its columns for mapping
            if self._original_columns:
                X_df = pd.DataFrame(X, columns=self._original_columns)
            else:
                # Fallback if original columns not stored (e.g., if fit was on numpy array)
                # This assumes order of features is preserved.
                X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        else:
            X_df = X

        # Check if all selected features are present in the input X_df
        missing_features = [f for f in self.selected_features_ if f not in X_df.columns]
        if missing_features:
            raise ValueError(f"Features {missing_features} were selected during fit but are missing in the input data for transform.")

        transformed_X = X_df[self.selected_features_]

        return transformed_X if is_dataframe_input else transformed_X.values

    def get_feature_names_out(self, input_features=None):
        """
        Returns the names of the selected features.

        Parameters
        ----------
        input_features : array-like of str or None, default=None
            Only used to validate that the number of input features matches
            the number of features seen during fit, if this was a DataFrame.
            Not directly used for output.

        Returns
        -------
        feature_names_out : ndarray of str
            Array with the names of the output features.
        """
        if self.selected_features_ is None:
            raise RuntimeError("RobustMRMRSelector not fitted yet.")
        return np.array(self.selected_features_)

    def _more_tags(self):
        """
        Scikit-learn tags for estimator checks and metadata.
        """
        return {
            'preserves_dm': True, # Preserves DataFrame if input is DataFrame
            'allow_nan': False, # feature_engine.MRMR doesn't handle NaNs by default
            'requires_y': True,
            'X_types': ['dataframe', 'numeric'],
            'y_type': ['binary', 'multiclass', 'continuous'],
            'poor_score': False,
            'no_validation': False # We do some basic validation
        }