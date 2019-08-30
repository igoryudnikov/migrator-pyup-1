import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="migrator",
    version="0.1.5preview",
    author="Vladyslav Barbanyagra",
    author_email="vbarbanyagra@griddynamics.com",
    description="Small package that provides utils for migrating py2 -> py3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vbarbanyagra-ias/smart2to3",
    packages=setuptools.find_packages(),
    install_requires=open('requirements.txt').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_data={
        'migrator': ['common/resources/*'],
    },
)
