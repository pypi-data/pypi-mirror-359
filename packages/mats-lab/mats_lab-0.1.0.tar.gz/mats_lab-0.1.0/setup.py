from setuptools import setup, find_packages

setup(
    name="mats_lab",
    version="0.1.0",
    description="Merged AI Tools System - unified access to AI tools and models",
    author="Assem Sabry",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "torch",
        "joblib",
        "transformers",
        "kaggle"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
