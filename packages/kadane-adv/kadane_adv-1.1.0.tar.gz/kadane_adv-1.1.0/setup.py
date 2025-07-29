from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kadane-adv",
    version="1.1.0",  # BUMP THIS!
    author="Parimal Kalpande , Krunal Wankhade",
    description="About An advanced Python library implementing Kadane’s Algorithm with support for 1D & 2D arrays, visualization, subarray constraints, and test coverage. Perfect for data analysis, time-series problems, and algorithm enthusiasts.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # or 'text/x-rst' if using .rst
    url="https://github.com/7pk5/kadane-adv",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)