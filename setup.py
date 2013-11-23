"""
CURD.py
-------

Tiny Python ORM for MySQL.

Sample Usage
````````````

.. code:: python

    from CURD import Database, Model, Field

    Database.config(user='root', passwd='', db='mytest')

    class User(Model):
        name = Field()
        email = Field()

    user = User(name='Join', email='Join@gmail.com')
    user.save()

Installation
````````````

.. code:: bash

    $ pip install CURD.py

Links
`````

* `documentation <http://curdpy.readthedocs.org/>`_
* `GitHub Repo <https://github.com/hit9/CURD.py>`_

**NOTICE**: CURD.py may not be stable before version 1.0

"""

from setuptools import setup


setup(
    name='CURD.py',
    version='0.3.4',
    author='hit9',
    author_email='nz2324@126.com',
    description=('Tiny Python ORM for MySQL'),
    license='BSD',
    keywords='CURD ORM MySQL Python tiny database',
    url='https://github.com/hit9/CURD.py',
    py_modules=['CURD'],
    install_requires = ['MySQL-python'],
    long_description=__doc__,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
