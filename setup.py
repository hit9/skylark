# -*- coding: utf-8 -*-

"""
skylark
-------

A micro python orm for mysql and sqlite.

Sample Usage
````````````

.. code:: python

    >>> from models import User
    >>> user = User(name='Tom', email='tom@gmail.com')
    >>> user.save()  # insert
    1
    >>> user.email = 'tom@github.com'
    >>> user.save()  # update
    1
    >>> [user.name for user in User.select()]  # select
    [u'Tom']
    >>> query = User.where(name='Tom').delete()
    >>> query.execute()  # delete
    1
    >>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
    >>> user.data
    {'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2}
    >>> user.destroy()  # another delete
    1

Installation
````````````

.. code:: bash

    $ pip install skylark

Links
`````

* `Documentation <http://skylark.readthedocs.org/>`_
* `Code on Github <https://github.com/hit9/skylark>`_

**NOTICE**: skylark may not be stable before version 1.0

"""

from setuptools import setup


setup(
    name='skylark',
    version='0.9.0',
    author='hit9',
    author_email='nz2324@126.com',
    description=('A micro python orm for mysql and sqlite.'),
    license='BSD',
    keywords='orm mysql sqlite tiny micro database',
    url='https://github.com/hit9/skylark',
    py_modules=['skylark'],
    long_description=__doc__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
