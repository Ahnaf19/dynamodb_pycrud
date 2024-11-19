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
    install_requires=[  # Specify dependency
        "boto3==1.35.57",
        "botocore==1.35.57",
        "jmespath==1.0.1",
        "s3transfer==0.10.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
