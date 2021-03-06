.. zgw_consumers documentation master file, created by startproject.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ZGW Consumers' documentation!
========================================

:Version: 0.13.0
:Source: https://github.com/maykinmedia/zgw-consumers
:Keywords: OpenAPI, Zaakgericht Werken, Common Ground, NLX
:PythonVersion: 3.6, 3.7, 3.8

|build-status| |requirements| |coverage|

|python-versions| |django-versions| |pypi-version|

Manage your external API's to consume.

.. contents::

.. section-numbering::

Features
========

* Store services with their configuration in the database
* Integrate with OpenAPI 3.0 specifications
* NLX support
* Declare data/domain objects as modern Python dataclasses

Installation
============

Requirements
------------

* Python 3.6 or newer
* setuptools 30.3.0 or newer
* Django 2.2 or newer


Install
-------

1. Install from PyPI

.. code-block:: bash

    pip install zgw-consumers

2. Add ``zgw_consumers`` to the ``INSTALLED_APPS`` setting.

3. Optionally override ``ZGW_CONSUMERS_CLIENT_CLASS`` to a custom client class.

4. Optionally specify ``ZGW_CONSUMERS_OAS_CACHE`` to point to a separate django cache.
   Defaults to ``django.core.cache.DEFAULT_CACHE_ALIAS``, which is ``default`` in
   practice. For performance reasons we highly recommend to use a real cache backend
   like Redis or Memcache.


Usage
=====

In the Django admin, you can create ``Service`` instances to define your external APIs.

**Client**

To get a client for a given resource, you can use:

.. code-block:: python

    from zgw_consumers.models import Service

    client = Service.get_client(some_url)

Or, to just retrieve the auth header(s):

.. code-block:: python

    from zgw_consumers.models import Service

    auth = Service.get_auth_header(some_url)

**Data model**

Use ``zgw_consumers.api_models.base.factory`` to turn raw JSON responses into instances
of domain models:

.. code-block:: python

    from zgw_consumers.api_models.base import factory
    from zgw_consumers.api_models.zaken import Zaak

    results = client.list("zaak")["results"]

    return factory(Zaak, results)


It works for both collections and scalar values, and takes care of the camel-case to
snake case conversion.


You can also define your own data models, take a look at the ``zgw_consumers.api_models``
package for inspiration.

.. |build-status| image:: https://travis-ci.org/maykinmedia/zgw-consumers.svg?branch=master
    :target: https://travis-ci.org/maykinmedia/zgw-consumers

.. |requirements| image:: https://requires.io/github/maykinmedia/zgw-consumers/requirements.svg?branch=master
    :target: https://requires.io/github/maykinmedia/zgw-consumers/requirements/?branch=master
    :alt: Requirements status

.. |coverage| image:: https://codecov.io/gh/maykinmedia/zgw-consumers/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/zgw-consumers
    :alt: Coverage status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/zgw_consumers.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/zgw_consumers.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/zgw_consumers.svg
    :target: https://pypi.org/project/zgw_consumers/
