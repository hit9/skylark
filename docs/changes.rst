.. _changes:

Changes
========

version 0.3.6
--------------

Added:

- Having

- Group By

version 0.3.5
-------------

No changes in API

- typofix

version 0.3.4
-------------

**not backward compatiable changes:**

Reomved:

- Removed method ``select_without_primarykey``

Changes:

- method ``select`` now won't select primarykeys automatically
- subquery parsing result now was wrapped with ``()``

version 0.3.3
--------------

Added Python types supporting:

- string, unicode
- numbers: float, int, long
- datetime: datetime, date, time, timedelta
- bool
- Nonetype
- sequence: list, tuple
- dict

version 0.3.2
-------------

Added:

- support for datetime

sample::

    >>> Post.at(1).update(update_at=datetime.now())
    <UpdateQuery "update post set post.update_at = '2013-11-21 16:45:57' where post.post_id = 1">

version 0.3.1
-------------

Added:

- Ability to use SQL functions

Supported SQL functions: ``count``, ``sum``, ``max``, ``min``, ``lcase``, ``ucase``
