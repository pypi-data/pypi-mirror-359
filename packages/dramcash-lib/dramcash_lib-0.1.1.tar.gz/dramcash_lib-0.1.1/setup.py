from setuptools import setup, find_packages

setup(
    name="dramcash_lib",  # This will be the pip package name
    version="0.1.1",
    description="Shared utility library for all microservices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sudhin M",
    author_email="sudhin.m@abilytics.com",
    url="https://github.com/sudhinm/dramcash_lib",  # Optional
    packages=find_packages(),  # 👈 Important: look inside src/
    include_package_data=True,
    install_requires=[
        "boto3",
        "pymongo",
        "pydantic-settings"
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)