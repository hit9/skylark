# -*- coding: utf-8 -*-

"""
skylark
-------

A nice micro orm for python, mysql only.

Sample Usage
````````````

.. code:: python

    >>> from models import User
    >>> user = User(name='Tom', email='tom@gmail.com')
    >>> user.save()  # insert
    1L
    >>> user.email = 'tom@github.com'
    >>> user.save()  # update
    1L
    >>> [user.name for user in User.select()]  # select
    [u'Tom']
    >>> query = User.where(name='Tom').delete()
    >>> query.execute()  # delete
    1L
    >>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
    >>> user.data
    {'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2L}
    >>> user.destroy()  # another delete
    1L

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
    version='0.7.1',
    author='hit9',
    author_email='nz2324@126.com',
    description=('A nice micro orm for python, mysql only.'),
    license='BSD',
    keywords='ORM MySQL Python tiny micro database',
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
