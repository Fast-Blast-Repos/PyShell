from setuptools import setup, find_packages

setup(
    name="PyShell",
    version="0.1.0",
    author="Your Name",
    description="A lightweight and customizable Python shell framework.",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Change if needed
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)

