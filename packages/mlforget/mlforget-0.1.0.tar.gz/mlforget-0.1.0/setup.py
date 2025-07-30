from setuptools import setup, find_packages

setup(
    name="mlforget",  # Make sure this is unique on PyPI
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "pandas",
        "scikit-learn"
    ],
    author="Kai Pinas",
    author_email="kai.pinas@student.uva.nl",
    description="Machine unlearning methods for energy consumption prediction",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Kaiboy55/MLForget",  # Or your homepage
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)