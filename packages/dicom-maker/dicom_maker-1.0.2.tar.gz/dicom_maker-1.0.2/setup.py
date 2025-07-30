import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dicom-maker",
    version="1.0.2",
    author="Aurabox",
    author_email="hello@aurabox.cloud",
    description="Enhanced DICOM Generator for creating sample DICOM studies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aurabx/dicom-maker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pathlib>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "dicom-maker=generators:main",
        ],
    },
)