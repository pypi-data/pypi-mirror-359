.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+

*******************************************************************************
                                    absence                                    
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/absence
   :alt: Package Version
   :target: https://pypi.org/project/absence/

.. image:: https://img.shields.io/pypi/status/absence
   :alt: PyPI - Status
   :target: https://pypi.org/project/absence/

.. image:: https://github.com/emcd/python-absence/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-absence/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-absence/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-absence/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-absence
   :alt: Project License
   :target: https://github.com/emcd/python-absence/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/absence
   :alt: Python Versions
   :target: https://pypi.org/project/absence/


🕳️ A Python library package which provides a **sentinel for absent values** - a
falsey, immutable singleton that represents the absence of a value in contexts
where ``None`` or ``False`` may be valid values.


Key Features ⭐
===============================================================================

* 1️⃣  **Absence Sentinel**: A falsey singleton which represents absence.
* 🏭 **Absence Factory**: Create custom absence sentinels for package-specific
  or arbitrary needs.
* 𝒇 **Predicate Functions**: Determine if a value is absent.
* 🔍 **Type Support**: Type alias for optional values which may be absent.
  (Similar to ``typing.Optional`` and its relation to ``None``.)
* 🌟 **Builtins Integration**: Can install singleton and predicate function
  into Python builtins.


Installation 📦
===============================================================================

::

    pip install absence


Examples 💡
===============================================================================

Use the ``absent`` sentinel to represent missing values:

>>> from dataclasses import dataclass
>>> from absence import absent, is_absent, Absential
>>> @dataclass
... class User:
...     name: str | None
...     email: str | None
>>> def apply_partial_update(
...     user: User,
...     name: Absential[ str | None ] = absent,
...     email: Absential[ str | None ] = absent,
... ) -> User:
...     ''' Updates user fields if values provided.
...
...         Absent value means "don't change".
...         None value means "clear field".
...     '''
...     if not is_absent( name ): user.name = name
...     if not is_absent( email ): user.email = email
...     return user
>>> user = User( name = 'Alice', email = 'alice@example.com' )
>>> # Clear name but leave email unchanged
>>> updated = apply_partial_update( user, name = None )
>>> updated.name  # Cleared to None
>>> updated.email  # Unchanged
'alice@example.com'
>>> # Update both fields
>>> updated = apply_partial_update( user, name = 'Bob', email = 'bob@example.com' )
>>> updated.name
'Bob'
>>> updated.email
'bob@example.com'

Create package-specific absence sentinels:

>>> from absence import AbsenceFactory
>>> MISSING = AbsenceFactory( )
>>> bool( MISSING )
False


Use Cases 🎯
===============================================================================

* 🔄 **Optional Arguments**: When ``None`` is a valid argument value but you
  need to detect absence.
* 🎯 **Sentinel Values**: When you need a unique, falsey object to represent
  missing or invalid states.
* 🧩 **Type Safety**: When you want explicit typing for values that may be
  absent.


Comparison with Alternatives 🤔
===============================================================================

+-------------------------+----------+---------+------------+------------+
| Alternative             | Truthy?  | Unique? | Picklable? | Scope      |
+=========================+==========+=========+============+============+
| ``object()``            | Yes      | Yes     | No         | Arbitrary  |
+-------------------------+----------+---------+------------+------------+
| PEP 661 Sentinels       | Optional | Yes     | Yes        | Per-Module |
+-------------------------+----------+---------+------------+------------+
| ``dataclasses.MISSING`` | Yes      | Yes     | No         | Global     |
+-------------------------+----------+---------+------------+------------+
| ``typing.NoDefault``    | Yes      | Yes     | Yes        | Global     |
+-------------------------+----------+---------+------------+------------+
| ``absence.absent``      | No       | Yes     | No         | Global     |
+-------------------------+----------+---------+------------+------------+

The ``absent`` sentinel combines falsey behavior with global uniqueness,
making it particularly suitable for representing missing values in contexts
where ``None`` might be a valid value. The companion ``AbsenceFactory``
allows creation of arbitrary absence sentinels, when needed, such as for
specific packages.

See `PEP 661 ("Sentinel Values") <https://peps.python.org/pep-0661/>`_,
`typing.NoDefault
<https://docs.python.org/3/library/typing.html#typing.NoDefault>`_, and
`dataclasses.MISSING
<https://docs.python.org/3/library/dataclasses.html#dataclasses.MISSING>`_ for
more details on alternatives.


`More Flair <https://www.imdb.com/title/tt0151804/characters/nm0431918>`_
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/python-absence
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-absence

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/pypi/implementation/absence
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/absence/

.. image:: https://img.shields.io/pypi/wheel/absence
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/absence/


Other Projects by This Author 🌟
===============================================================================


* `python-accretive <https://github.com/emcd/python-accretive>`_ (`accretive <https://pypi.org/project/accretive/>`_ on PyPI) 

  🌌 A Python library package which provides **accretive data structures** - collections which can grow but never shrink.
* `python-classcore <https://github.com/emcd/python-classcore>`_ (`classcore <https://pypi.org/project/classcore/>`_ on PyPI) 

  🏭 A Python library package which provides **foundational class factories and decorators** for providing classes with attributes immutability and concealment and other custom behaviors.
* `python-dynadoc <https://github.com/emcd/python-dynadoc>`_ (`dynadoc <https://pypi.org/project/dynadoc/>`_ on PyPI) 

  📝 A Python library package which bridges the gap between **rich annotations** and **automatic documentation generation** with configurable renderers and support for reusable fragments.
* `python-falsifier <https://github.com/emcd/python-falsifier>`_ (`falsifier <https://pypi.org/project/falsifier/>`_ on PyPI) 

  🎭 A very simple Python library package which provides a **base class for falsey objects** - objects that evaluate to ``False`` in boolean contexts.
* `python-frigid <https://github.com/emcd/python-frigid>`_ (`frigid <https://pypi.org/project/frigid/>`_ on PyPI) 

  🔒 A Python library package which provides **immutable data structures** - collections which cannot be modified after creation.
* `python-icecream-truck <https://github.com/emcd/python-icecream-truck>`_ (`icecream-truck <https://pypi.org/project/icecream-truck/>`_ on PyPI) 

  🍦 **Flavorful Debugging** - A Python library which enhances the powerful and well-known ``icecream`` package with flavored traces, configuration hierarchies, customized outputs, ready-made recipes, and more.
* `python-mimeogram <https://github.com/emcd/python-mimeogram>`_ (`mimeogram <https://pypi.org/project/mimeogram/>`_ on PyPI) 

  📨 A command-line tool for **exchanging collections of files with Large Language Models** - bundle multiple files into a single clipboard-ready document while preserving directory structure and metadata... good for code reviews, project sharing, and LLM interactions.
