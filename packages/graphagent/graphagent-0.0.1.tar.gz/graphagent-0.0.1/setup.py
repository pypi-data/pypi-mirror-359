from setuptools import setup, find_packages

setup(
    name="graphagent",
    version="0.0.1",
    author="GraphAgent",
    author_email="hey@graphagent.dev",
    description="GraphAgent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
