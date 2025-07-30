import setuptools

# Load the long_description from README.md
with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="microkan",
    version="0.1.0",
    author="Alireza Afzal Aghaei",
    author_email="alirezaafzalaghaei@gmail.com",
    description="A Kolmogorov Arnold Network for Edge Devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alirezaafzalaghaei/microkan",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
