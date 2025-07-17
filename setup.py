#!/usr/bin/env python3
"""
Setup script for the Photo Organizer application.
"""

from setuptools import find_packages, setup

with open("README.txt", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="photo-organizer",
    version="0.1.0",
    author="Photo Organizer Team",
    author_email="example@example.com",
    description="An application to intelligently organize and rename image files",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/example/photo-organizer",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "photo-organizer=photo_organizer.main:main",
        ],
    },
)