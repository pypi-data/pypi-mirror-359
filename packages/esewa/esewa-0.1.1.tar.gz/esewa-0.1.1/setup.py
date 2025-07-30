from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="esewa",  
    version="0.1.1",         
    author="Sahil Dahal",
    author_email="the.sahil.verse@gmail.com",
    description="Python package for integrating eSewa payment gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sahilverse/esewa-python", 
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
    install_requires=[
        "requests>=2.25.1", 
    ],
)
