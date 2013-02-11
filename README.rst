=======
Sixpack
=======

.. image:: https://travis-ci.org/seatgeek/sixpack.png?branch=master
        :target: https://travis-ci.org/seatgeek/sixpack

Sixpack is a tool to help solve the problem of A/B testing across multiple programming languages. It does this by exposing a very simple API that a client library in virtually any language can make requests against.

Sixpack is comprised of two main parts. The first is Sixpack server which is responsible for responding to web requests, and the second is (an optional) Sixpack-Web which will allow you to access the Sixpack dashboard for seeing and acting on your A/B tests.

============
Requirements
============

* Redis
* Python >= 2.7 (3.0 Untested, Pull Requests welcome)

===============
Getting Started
===============

To get going create (or don't, but you really should) a new virtualenv for your sixpack installation. Follow that up with a ``pip install``::

    $ pip install sixpack

Next you're going to need to create a Sixpack configuration file that specificies a few things. Here's the default::

    redis_port: 6379
    redis_host: localhost
    redis_prefix: sixpack
    redis_db: 15

    full_response: True

    robot_regex: $^|trivial|facebook|MetaURI|butterfly|google|amazon|goldfire|sleuth|xenu|msnbot|SiteUptime|Slurp|WordPress|ZIBB|ZyBorg|pingdom|bot|yahoo|slurp|java|fetch|spider|url|crawl|oneriot|abby|commentreader|twiceler
    ignored_ip_addresses: []
    control_on_db_failure: True
    allow_multiple_experiments: False

    secret_key: '<your secret key here>'

You can store this file anywhere, we'd like to reccomment ``/etc/sixpack/config.yml``, but where ever you'd like to store it is fine. As long as Redis is running, you should now beable to start the Sixpack servers like this::

    $ SIXPACK_CONFIG=<path to config.yml> sixpack

and::

    $ SIXPACK_CONFIG=<path to config.yml> sixpack-web

Sixpack Server and Sixpack Web will be listing on ports 5000 and 5001 respectively. For use in a production enviroment, please see the "Production Notes" section below.

=====
Usage
=====

All interaction with Sixpack is done via ``HTTP GET`` requests. Sixpack allows for cross-language testing by accepting a unique ``client_id`` (which the client is responsible for generating) that links a participation to a conversion. All requests to Sixpack require a ``client_id``.

Participating in an Experiment
------------------------------

You can participate in an experiment with a ``GET`` request such as::

    $ curl http://localhost:5000/participate?experiment=button_color&alternatives=red&alternatives=blue&alternatives=orange&client_id=user-2

If the test does not exist, it will be created automatically.

``experiment`` (required) is the name of the test you'd like to start A/B testing. Valid Experiment names must be alphanumeric and can contain ``_`` and ``-``.

``alternatives`` (required) are the potential responses from Sixpack, and will be the bucket that the ``client_id`` is assigned to.

``client_id`` (required) is the unique id for the user participating in the test.

Notes
`````

These are some notes

Production Notes
================

We reccomend running Sixpack on gunicorn in production. You will need to install gunicorn in your virtual environment before running the following.

To run the sixpack server using gunicorn/gevent - a separate installation - you can run the following::

    gunicorn --access-logfile - -w 8 --worker-class=gevent sixpack.server:start

To run the sixpack web dashboard using gunicorn/gevent - a separate installation - you can run the following::

    gunicorn --access-logfile - -w 2 --worker-class=gevent sixpack.web:start

