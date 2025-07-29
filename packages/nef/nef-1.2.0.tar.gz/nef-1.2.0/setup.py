import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nef",
    version="1.2.0",
    author="Andy Klier",
    author_email="andyklier@gmail.com",
    description="CLI (simple command line client) for AWS cloudwatch logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/shindagger/nef",
    license="MIT",
    packages = ['nef'],
    install_requires= ['setuptools', 'string-color>=0.2.7'],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': ['nef=nef.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
