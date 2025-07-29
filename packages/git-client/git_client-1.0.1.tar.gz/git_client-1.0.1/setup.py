import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-client",
    version="1.0.1",
    author="Andy Klier",
    author_email="andyklier@gmail.com",
    description="gc is a command line helper client for using git.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/shindagger/git-client",
    license="MIT",
    packages=['gitclient'],
    include_package_data=True,
    install_requires= ['setuptools', 'inquirer', 'string-color>=0.2.7'],
    entry_points = {
        'console_scripts': ['gc=gitclient.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
