from setuptools import setup, find_packages

setup(
    name='pyrobustfs',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'scikit-learn>=0.23.0',
        'feature-engine>=1.0.0',
    ],
    author='Manoj Kumar',
    author_email='manojkumar.du.or.21@gmail.com',
    description='A robust feature selection library using ensemble mRMR and optional refinement.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/manojkumar010/pyrobustfs',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.7',
)
