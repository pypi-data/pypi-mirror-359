import setuptools

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mathkit_vg",
    version="0.1.0",
    author="Vijaya Giduthuri",
    author_email="vijayagiduthuri2@gmail.com",
    description="A Python package with essential number utilities and math tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires='>=3.6',
    install_requires=[],
)
