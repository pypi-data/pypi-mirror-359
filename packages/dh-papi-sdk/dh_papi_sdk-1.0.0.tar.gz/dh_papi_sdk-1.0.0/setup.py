import setuptools
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# The version is managed in papi_sdk/__init__.py
with open(os.path.join("papi_sdk", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name="dh-papi-sdk",
    version=version,
    author="Delivery Hero",
    description="Python SDK for Salesforce Platform API (PAPI)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deliveryhero/dh-sf-pa-apigee",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests >= 2.25.0",
        "pydantic >= 2.0.0, < 3.0.0",
        "typing-extensions >= 4.7.1",
        "urllib3 >= 1.26.0, < 1.27.0",  # Fixed version range
        "python-dateutil >= 2.8.0",
        "certifi >= 2021.5.25",
    ]
)
