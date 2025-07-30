from setuptools import setup, find_packages

setup(
    name='sfdl-cluster',
    version='0.1.0',
    description='Same Features Different Label clustering tool with Calinski-Harabasz score',
    author='Your Name',
    author_email='you@example.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'scikit-learn'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
