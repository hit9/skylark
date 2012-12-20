from setuptools import setup

setup(
    name = "virgo",
    version = "0.1.1",
    author = "hit9",
    author_email = "nz2324@126.com",
    description = ("Simple & Easy to use ORM for Python & MySQL"),
    license = "BSD",
    keywords = "ORM MySQL Python database virgo",
    url = "https://github.com/hit9/virgo",
    py_modules=['virgo'],
    install_requires = ['MySQL-python'],
)
