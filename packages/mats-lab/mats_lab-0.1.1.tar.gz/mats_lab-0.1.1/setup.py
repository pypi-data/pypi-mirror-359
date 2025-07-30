from setuptools import setup, find_packages

setup(
    name="mats_lab",
    version="0.1.1",
    description="Merged AI Tools System - Developed by Assem Sabry",
    author="Assem Sabry",
    author_email="assem7sabry@gmail.com",
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
