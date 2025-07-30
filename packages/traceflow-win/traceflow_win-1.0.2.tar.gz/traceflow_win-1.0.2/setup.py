import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="traceflow-win",
    version="1.0.2",
    author="Salem Shreve",
    author_email="salemshreve02@gmail.com",
    description = "A windows compatible path tracing package based off the functionality of rucarrol's traceflow.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sshreve0/traceflow_win",
    license= "LICENSE",
    python_requires=">=3.10",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    #package_data={"": ["var/*.html"]},
    entry_points={"console_scripts": ["traceflow-win=traceflow_win.__main__:main"]},
)