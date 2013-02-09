from setuptools import setup

setup(
    name="CURD.py",
    version="0.2.1",
    author="hit9",
    author_email="nz2324@126.com",
    description=("Tiny Python ORM for MySQL"),
    license="BSD",
    keywords="CURD ORM MySQL Python tiny database",
    url="https://github.com/hit9/CURD.py",
    py_modules=['CURD'],
    install_requires = ['MySQL-python'],
)
