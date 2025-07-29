from setuptools import setup, find_packages

# Read the long description from your README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="encrypted_text_search",
    version="0.2.1",  # <-- Increment for every new upload!
    author="Wangchen T T",
    author_email="wangchentt.cy23@rvce.edu.in",
    description="Efficient Privacy-Preserving Search in Encrypted Databases using Heapsort and String Matching Techniques",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/encrypted_text_search",  # (optional, add if you use GitHub)
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "cryptography>=3.0",
        "matplotlib>=3.0"
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "encrypted-text-search=encrypted_text_search.main:menu"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ],
    license="MIT",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/encrypted_text_search/issues",
        "Documentation": "https://github.com/yourusername/encrypted_text_search#readme",
    }
)
