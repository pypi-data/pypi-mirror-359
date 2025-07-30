from setuptools import setup, find_packages

setup(
    name="mycelium_forest",
    version="1.0.0",
    author="Derya Kapisiz",
    author_email="dkapisiz.data@gmail.com",
    description="Visualize Random Forest trees with mycelium-inspired network representations",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.3.0",
        "scipy>=1.7.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)