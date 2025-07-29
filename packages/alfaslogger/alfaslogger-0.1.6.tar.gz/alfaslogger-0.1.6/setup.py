from setuptools import setup

setup(
    name="alfaslogger",
    version="0.1.6",
    py_modules=["logger_app"],
    author="TcAlfa31",
    author_email="sosyalfaone@gmail.com",
    description="Web GUI destekli Alfaslogger paketi",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TheAlfa31",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
    "websockets>=10.0"
    ]
)
