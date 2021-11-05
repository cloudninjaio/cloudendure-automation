import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloudendure2",
    version="0.0.4",
    author="Christian Mendez",
    description="A python wrapper for the CloudEndure API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    platforms="Any",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)