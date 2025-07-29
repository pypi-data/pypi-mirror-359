from setuptools import setup, find_packages

setup(
    name="sldf_splitter",
    version="0.1.0",
    description="Same Label, Different Features (SLDF) data partitioning tool",
    author="Your Name",
    packages=find_packages(),
    install_requires=["pandas"],
    python_requires='>=3.7',
)
