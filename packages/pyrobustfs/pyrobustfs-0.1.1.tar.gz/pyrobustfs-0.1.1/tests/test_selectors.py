import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.feature_selection import RFE, SelectKBest, f_classif, f_regression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pyrobustfs.selectors import RobustMRMRSelector

# Fixtures for common test data
@pytest.fixture
def classification_data():
    X, y = make_classification(n_samples=100, n_features=20, n_informative=5, n_redundant=2, random_state=42)
    X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    return X, y

@pytest.fixture
def regression_data():
    X, y = make_regression(n_samples=100, n_features=20, n_informative=5, random_state=42)
    X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    return X, y

# Test basic functionality
def test_basic_classification_selection(classification_data):
    X, y = classification_data
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, classification=True, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)

    assert X_transformed.shape[1] == 5
    assert isinstance(X_transformed, pd.DataFrame)
    assert len(selector.selected_features_) == 5
    assert all(f in X.columns for f in selector.selected_features_)

def test_basic_regression_selection(regression_data):
    X, y = regression_data
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, classification=False, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)

    assert X_transformed.shape[1] == 5
    assert isinstance(X_transformed, pd.DataFrame)
    assert len(selector.selected_features_) == 5
    assert all(f in X.columns for f in selector.selected_features_)

# Test different n_features_to_select
def test_n_features_to_select(classification_data):
    X, y = classification_data
    n_features = 3
    selector = RobustMRMRSelector(n_features_to_select=n_features, n_ensembles=5, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == n_features
    assert len(selector.selected_features_) == n_features

# Test different n_ensembles
def test_n_ensembles(classification_data):
    X, y = classification_data
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=10, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 5

# Test subsample_ratio
def test_subsample_ratio(classification_data):
    X, y = classification_data
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, subsample_ratio=0.7, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 5

# Test with refiner_estimator (RFE)
def test_refiner_rfe(classification_data):
    X, y = classification_data
    refiner = RFE(estimator=LogisticRegression(solver='liblinear', random_state=42), n_features_to_select=5)
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, refiner_estimator=refiner, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 5
    assert len(selector.selected_features_) == 5

# Test with refiner_estimator (SelectKBest) - regression
def test_refiner_selectkbest_regression(regression_data):
    X, y = regression_data
    refiner = SelectKBest(score_func=f_regression, k=5) # Use f_regression for regression tasks
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, refiner_estimator=refiner, classification=False, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 5
    assert len(selector.selected_features_) == 5

# Test input as NumPy array
def test_numpy_input(classification_data):
    X, y = classification_data
    X_np = X.values
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, random_state=42)
    selector.fit(X_np, y)
    X_transformed = selector.transform(X_np)

    assert X_transformed.shape[1] == 5
    assert isinstance(X_transformed, np.ndarray)
    assert len(selector.selected_features_) == 5
    # When input is numpy, selected_features_ will be generic names
    assert all(f.startswith('feature_') for f in selector.selected_features_)

# Test transform before fit
def test_transform_before_fit_raises_error(classification_data):
    X, y = classification_data
    selector = RobustMRMRSelector(n_features_to_select=5)
    with pytest.raises(RuntimeError, match="RobustMRMRSelector not fitted yet. Call fit\(\) first."):
        selector.transform(X)

# Test invalid n_features_to_select
def test_invalid_n_features_to_select_raises_error():
    with pytest.raises(ValueError, match="n_features_to_select must be a positive integer."):
        RobustMRMRSelector(n_features_to_select=0)
    with pytest.raises(ValueError, match="n_features_to_select must be a positive integer."):
        RobustMRMRSelector(n_features_to_select=-1)

# Test n_features_to_select greater than available features
def test_n_features_greater_than_total_raises_error(classification_data):
    X, y = classification_data
    with pytest.raises(ValueError, match="n_features_to_select \(.*\) cannot be greater than the number of features in X \(.*\)."):
        selector = RobustMRMRSelector(n_features_to_select=X.shape[1] + 1, n_ensembles=5, random_state=42)
        selector.fit(X, y)

# Test invalid subsample_ratio
def test_invalid_subsample_ratio_raises_error():
    with pytest.raises(ValueError, match="subsample_ratio must be between 0 \(exclusive\) and 1 \(inclusive\)."):
        RobustMRMRSelector(subsample_ratio=0.0)
    with pytest.raises(ValueError, match="subsample_ratio must be between 0 \(exclusive\) and 1 \(inclusive\)."):
        RobustMRMRSelector(subsample_ratio=1.1)

# Test invalid mrmr_scheme
def test_invalid_mrmr_scheme_raises_error():
    with pytest.raises(ValueError, match="mrmr_scheme must be 'MID' or 'MIQ'."):
        RobustMRMRSelector(mrmr_scheme='INVALID')

# Test get_feature_names_out
def test_get_feature_names_out(classification_data):
    X, y = classification_data
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, random_state=42)
    selector.fit(X, y)
    feature_names = selector.get_feature_names_out()
    assert isinstance(feature_names, np.ndarray)
    assert len(feature_names) == 5
    assert all(isinstance(f, str) for f in feature_names)

# Test refiner as a Pipeline (e.g., with StandardScaler)
def test_refiner_pipeline(classification_data):
    X, y = classification_data
    refiner_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('logreg', LogisticRegression(solver='liblinear', random_state=42))
    ])
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, refiner_estimator=refiner_pipeline, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 5

# Test that refiner_estimator's n_features_to_select is respected if set
def test_refiner_n_features_to_select_respected(classification_data):
    X, y = classification_data
    # RFE will select 3 features, even if RobustMRMRSelector asks for 5
    refiner = RFE(estimator=LogisticRegression(solver='liblinear', random_state=42), n_features_to_select=3)
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, refiner_estimator=refiner, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 3 # Should be 3, as RFE dictates
    assert len(selector.selected_features_) == 3

# Test that refiner_estimator's k is respected if set (for SelectKBest)
def test_refiner_k_respected(classification_data):
    X, y = classification_data
    # SelectKBest will select 4 features, even if RobustMRMRSelector asks for 5
    refiner = SelectKBest(score_func=f_classif, k=4)
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, refiner_estimator=refiner, random_state=42)
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    assert X_transformed.shape[1] == 4 # Should be 4, as SelectKBest dictates
    assert len(selector.selected_features_) == 4

# Test missing features in transform
def test_missing_features_in_transform_raises_error(classification_data):
    X, y = classification_data
    selector = RobustMRMRSelector(n_features_to_select=5, n_ensembles=5, random_state=42)
    selector.fit(X, y)

    # Create a new DataFrame with a missing feature
    X_test_missing = X.drop(columns=[selector.selected_features_[0]])

    with pytest.raises(ValueError, match="Features .* were selected during fit but are missing in the input data for transform."):
        selector.transform(X_test_missing)
