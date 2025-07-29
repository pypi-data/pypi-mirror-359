from setuptools import setup, find_packages

setup(
    name="encrypted_text_search",
    version="0.1.0",
    description="Efficient Privacy-Preserving Search in Encrypted Databases using Heapsort and String Matching Techniques",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "cryptography",
        "matplotlib"
    ],
    entry_points={
        "console_scripts": [
            "encrypted-text-search=encrypted_text_search.main:menu"
        ]
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
