import setuptools
import pathlib

setuptools.setup(
    name="ants_fts",
    version="0.2.3",
    description="This library is used to extract features from data.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://ants.abc",
    author="HaoPP",
    author_email="haopp@antsomi.com",
    project_urls={
        "Source": "https://ants.abc/source",  # Replace with actual URL to source
        "Documentation": "https://ants.abc/docs",  # Add a documentation URL if available
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",  # Specify more versions if needed
        "License :: OSI Approved :: MIT License",  # Adjust the license if necessary
        "Operating System :: OS Independent",  # Ensure compatibility with all systems
        "Intended Audience :: Developers",  # If it's targeted at developers
        "Natural Language :: English",  # Specify language
    ],
    packages=setuptools.find_packages(),  # Automatically find packages in your directory
    install_requires=[
        "numpy",  # Adding numpy as a dependency
        "pandas",  # Adding pandas as a dependency
    ],
    python_requires=">=3.7",  # Adjust this according to your supported Python versions
)