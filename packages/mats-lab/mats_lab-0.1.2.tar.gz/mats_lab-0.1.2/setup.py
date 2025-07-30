from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mats_lab",
    version="0.1.2",
    description="Unified AI Interface - Merged AI Tools System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Assem Sabry",
    author_email="assem7sabry@gmail.com",
    url="https://github.com/assemsabry/mats-lab",
    packages=find_packages(),
    install_requires=[
        "torch",
        "tensorflow",
        "scikit-learn",
        "transformers",
        "datasets",
        "peft",
        "kaggle",
        "joblib",
        "numpy",
        "matplotlib",
        "seaborn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mats = mats_lab.__main__:main"
        ]
    },
)
