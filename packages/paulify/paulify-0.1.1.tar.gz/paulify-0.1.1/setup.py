from setuptools import setup, find_packages

setup(
    name="paulify",
    version="0.1.1",
    description="PAUL v1.1 license attribution helper",
    author="Marty L. Danish",
    author_email="Hello@MartyDoesData.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "paulify=paulify.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",  # You can customize or leave as placeholder
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)