from setuptools import setup, find_packages

setup(
    name="dynamodb_pycrud",  # Package name
    version="0.1.0",  # Initial version
    description="A Python CRUD library for AWS DynamoDB using boto3.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ahnaf19",
    author_email="ahnaftanjid19@gmail.com",
    url="https://github.com/Ahnaf19/dynamodb_pycrud.git",
    packages=find_packages(),  # Automatically find package directories
    install_requires=["boto3>=1.28.0", "botocore>=1.28.0"],  # Specify boto3 dependency
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
