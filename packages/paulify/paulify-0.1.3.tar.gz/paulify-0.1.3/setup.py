from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="paulify",
    version="0.1.3",
    description="PAUL v1.1 license attribution helper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marty L. Danish (cactusflatscoder)",
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