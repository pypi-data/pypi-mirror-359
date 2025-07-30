from setuptools import setup, find_packages

setup(
    name="shelvr",
    version="0.1.0",
    description="A smart CLI file organizer that cleans clutter",
    author="Vaibhav Tiwari",
    packages=find_packages(),
    install_requires=["colorama"],
    entry_points={
        "console_scripts": [
            "shelvr = shelvr.cli:main",
        ]
    },
    python_requires=">=3.6",
)
