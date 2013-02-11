Sixpack
=======

.. image:: https://travis-ci.org/seatgeek/sixpack.png?branch=master
        :target: https://travis-ci.org/seatgeek/sixpack

Sixpack is a tool to help solve the problem of A/B testing across multiple programming languages. It does this by exposing a very simple API that a client library in virtually any language can make requests against.

Sixpack is comprised of two main parts. The first is Sixpack server which is responsible for responding to web requests, and the second is (an optional) Sixpack-Web which will allow you to access the Sixpack dashboard for seeing and acting on your A/B tests.

Requirements
============

* Redis
* Python >= 2.7 (3.0 Untested, Pull Requests welcome)

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

Deployment
==========

Production Notes
----------------

To run the sixpack server using gunicorn/gevent - a separate installation - you can run the following::

    gunicorn --access-logfile - -w 8 --worker-class=gevent sixpack.server:start

To run the sixpack web dashboard using gunicorn/gevent - a separate installation - you can run the following::

    gunicorn --access-logfile - -w 2 --worker-class=gevent sixpack.web:start

Starting Sixpack (Developement)
-------------------------------

To start the sixpack server in development mode::

    cd sixpack
    # virtualenv here, if you want
    pip install -r requirements.txt
    PYTHONPATH=. SIXPACK_CONFIG=config.yml bin/sixpack

The sixpack server will be accessible at ``localhost:5000``

To seed some random data::

    cd sixpack
    # create a virtualenv here, if you want
    pip install -r requirements.txt
    bin/sixpack-seed # (with above server running)

Starting Sixpack-Web (Development)
----------------------------------

To start the sixpack web dashboard in development mode::

    cd sixpack
    # virtualenv here, if you want
    pip install -r requirements.txt
    PYTHONPATH=. SIXPACK_CONFIG=config.yml bin/sixpack-web


The sixpack web dashboard will be accessible at ``localhost:5001``
