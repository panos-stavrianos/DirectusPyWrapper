import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="DirectusPyWrapper",  # Replace with your own username
    version="0.0.1",
    author="Panos Stavrianos",
    description="A python wrapper for Directus API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/panos-stavrianos/DirectusPyWrapper",
    packages=setuptools.find_packages(),
    classifiers=["directus", "wrapper", "api"],
    python_requires='>=3.6',
)
