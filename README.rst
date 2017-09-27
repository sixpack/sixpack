=======
Sixpack
=======


.. image:: https://travis-ci.org/seatgeek/sixpack.png?branch=master
    :target: https://travis-ci.org/seatgeek/sixpack

.. image:: https://coveralls.io/repos/seatgeek/sixpack/badge.png?branch=master
    :target: https://coveralls.io/r/seatgeek/sixpack?branch=master

Sixpack is a framework to enable A/B testing across multiple programming languages. It does this by exposing a simple API for client libraries.  Client libraries can be written in virtually any language.

Sixpack has two main parts. The first, **Sixpack-server**, is responsible for responding to web requests.  The second, **Sixpack-web**, is a web dashboard for tracking and acting on your A/B tests.  Sixpack-web is optional.

Requirements
============

* Redis >= 2.6
* Python >= 2.7 (3.0 untested, pull requests welcome)

Getting Started
===============

To get going, create (or don't, but you really should) a new virtualenv for your Sixpack installation. Follow that up with ``pip install``::

    $ pip install sixpack


**Note:** If you get an error like ``src/hiredis.h:4:20: fatal error: Python.h: No such file or directory`` you need to install the python development tools. ``apt-get install python-dev`` on Ubuntu.

Next, create a Sixpack configuration. A configuration must be created for Sixpack to run. Here's the default::

    redis_port: 6379                            # Redis port
    redis_host: localhost                       # Redis host
    redis_prefix: sixpack                       # all Redis keys will be prefixed with this
    redis_db: 15                                # DB number in redis

    metrics: false                              # send metrics to StatsD (response times, # of calls, etc)?
    statsd_url: 'udp://localhost:8125/sixpack'  # StatsD url to connect to (used only when metrics: true)

    # The regex to match for robots
    robot_regex: $^|trivial|facebook|MetaURI|butterfly|google|amazon|goldfire|sleuth|xenu|msnbot|SiteUptime|Slurp|WordPress|ZIBB|ZyBorg|pingdom|bot|yahoo|slurp|java|fetch|spider|url|crawl|oneriot|abby|commentreader|twiceler
    ignored_ip_addresses: []                    # List of IP

    asset_path: gen                             # Path for compressed assets to live. This path is RELATIVE to sixpack/static
    secret_key: '<your secret key here>'        # Random key (any string is valid, required for sixpack-web to run)

You can store this file anywhere (we recommend ``/etc/sixpack/config.yml``). As long as Redis is running, you can now start the Sixpack server like this::

    $ SIXPACK_CONFIG=<path to config.yml> sixpack

Sixpack-server will be listening on port 5000 by default but can be changed with the ``SIXPACK_PORT`` environment variable. For use in a production environment, please see the "Production Notes" section below.

Alternatively, as of version 1.1, all Sixpack configuration can be set by environment variables. The following environment variables are available:

* ``SIXPACK_CONFIG_ENABLED``
* ``SIXPACK_CONFIG_REDIS_PORT``
* ``SIXPACK_CONFIG_REDIS_HOST``
* ``SIXPACK_CONFIG_REDIS_PASSWORD``
* ``SIXPACK_CONFIG_REDIS_PREFIX``
* ``SIXPACK_CONFIG_REDIS_DB``
* ``SIXPACK_CONFIG_ROBOT_REGEX``
* ``SIXPACK_CONFIG_IGNORE_IPS`` - comma separated
* ``SIXPACK_CONFIG_ASSET_PATH``
* ``SIXPACK_CONFIG_SECRET``
* ``SIXPACK_CORS_ORIGIN``
* ``SIXPACK_CORS_HEADERS``
* ``SIXPACK_CORS_CREDENTIALS``
* ``SIXPACK_CORS_METHODS``
* ``SIXPACK_CORS_EXPOSE_HEADERS``
* ``SIXPACK_METRICS``
* ``STATSD_URL``

Using the API
=============

All interaction with Sixpack is done via ``HTTP GET`` requests. Sixpack allows for cross-language testing by accepting a unique ``client_id`` (which the client is responsible for generating) that links a participation to a conversion. All requests to Sixpack require a ``client_id``.

The Sixpack API can be used from front-end Javascript via CORS-enabled requests. The Sixpack API server will accept CORS requests from any domain.

Participating in an Experiment
------------------------------

You can participate in an experiment with a ``GET`` request to the ``participate`` endpoint::

    $ curl http://localhost:5000/participate?experiment=button_color&alternatives=red&alternatives=blue&client_id=12345678-1234-5678-1234-567812345678

If the test does not exist, it will be created automatically.  You do not need to create the test in Sixpack-web.

    Experiment names are not validated, so it is possible to explode the Redis keyspace.
    If you need to validate that the experiments being created are only those you wish to
    whitelist, consider fronting Sixpack with either `Nginx+Lua`/`Openresty` or `Varnish`,
    and performing your whitelisting logic there.

Arguments
---------

``experiment`` (required) is the name of the test. Valid experiment names must be a lowercase alphanumeric string and can contain ``_`` and ``-``.

``alternatives`` (required) are the potential responses from Sixpack.  One of them will be the bucket that the ``client_id`` is assigned to.

``client_id`` (required) is the unique id for the user participating in the test.

``user_agent`` (optional) user agent of the user making a request. Used for bot detection.

``ip_address`` (optional) IP address of user making a request. Used for bot detection.

``force`` (optional) force a specific alternative to be returned, example::

    $ curl http://localhost:5000/participate?experiment=button_color&alternatives=red&alternatives=blue&force=red&client_id=12345678-1234-5678-1234-567812345678

In this example, red will always be returned. This is used for testing only, and no participation will be recorded.

``record_force`` (optional) for use with ``force``, participation will be recorded.

``traffic_fraction`` (optional) Sixpack allows for limiting experiments to a subset of traffic. You can pass the percentage of traffic you'd like to expose the test to as a decimal number here. (``?traffic_fraction=0.10`` for 10%)


Response
--------

A typical Sixpack participation response will look something like this::

    {
        status: "ok",
        alternative: {
            name: "red"
        },
        experiment: {
            name: "button_color"
        },
        client_id: "12345678-1234-5678-1234-567812345678"
    }

The most interesting part of this is ``alternative``. This is a representation of the alternative that was chosen for the test and assigned to a ``client_id``. All subsequent requests to this experiment/client_id combination will be returned the same alternative.

Converting a user
-----------------

You can convert a user with a ``GET`` request to the ``convert`` endpoint::

    $ curl http://localhost:5000/convert?experiment=button_color&client_id=12345678-1234-5678-1234-567812345678

Conversion Arguments
--------------------

- ``experiment`` (required) the name of the experiment you would like to convert on.
- ``client_id`` (required) the client you would like to convert.
- ``kpi`` (optional) sixpack supports recording multiple KPIs. If you would like to track conversion against a specfic KPI, you can do that here. If the KPI does not exist, it will be created automatically.

Notes
-----

You'll notice that the ``convert`` endpoint does not take an ``alternative`` query parameter. This is because Sixpack handles that internally with the ``client_id``.

We've included a 'health-check' endpoint, available at ``/_status``. This is helpful for monitoring and alerting if the Sixpack service becomes unavailable. The health check will respond with either 200 (success) or 500 (failure) headers.

Clients
=======

We've already provided clients in four languages. We'd love to add clients in additional languages.  If you feel inclined to create one, please first read the CLIENTSPEC_.  After writing your client, please update and pull request this file so we know about it.

- Ruby_
- Python_
- JavaScript_
- PHP_
- iOS_
- Go_
- Perl_
- `C#`_
- `Java/Android`_

.. _Ruby: http://github.com/seatgeek/sixpack-rb
.. _Python: http://github.com/seatgeek/sixpack-py
.. _JavaScript: http://github.com/seatgeek/sixpack-js
.. _PHP: http://github.com/seatgeek/sixpack-php
.. _iOS: http://github.com/seatgeek/sixpack-ios
.. _Go: http://github.com/subosito/sixpack-go
.. _Perl: http://github.com/b10m/p5-WWW-Sixpack
.. _C#: https://github.com/nderraugh/sixpack-cs
.. _Java/Android: http://github.com/seatgeek/sixpack-java

Algorithm
=========

As of version 2.0 of Sixpack, we use a deterministic algorithm to choose which alternative a client will receive. The algorithm was ported from Facebook's Planout project, and more information can be found HERE_.




Dashboard
=========

Sixpack comes with a built in dashboard. You can start the dashboard with::

    $ SIXPACK_CONFIG=<path to config.yml> sixpack-web

The Sixpack dashboard allows you to visualize how each experiment's alternatives are doing compared to the rest, select alternatives as winners, and update experiment descriptions to something more human-readable.

Sixpack-web defaults to run on port ``5001`` but can be changed with the ``SIXPACK_WEB_PORT`` environment variable. Sixpack-web will not work properly until you set the ``secret_key`` variable in the configuration file.

API
---

Sixpack web dashboard has a bit of a read-only API built in. To get a list of all experiment information you can make a request like::

    $ curl http://localhost:5001/experiments.json

To get the information for a single experiment, you can make a request like::

    $ curl http://localhost:5001/experiments/blue-or-red-header.json

Production Notes
================

We recommend running Sixpack on gunicorn_ in production. You will need to install gunicorn in your virtual environment before running the following.

To run the sixpack server using gunicorn/gevent (a separate installation) you can run the following::

    gunicorn --access-logfile - -w 8 --worker-class=gevent sixpack.server:start

To run the sixpack web dashboard using gunicorn/gevent (a separate installation) you can run the following::

    gunicorn --access-logfile - -w 2 --worker-class=gevent sixpack.web:start

**Note:** After selecting an experiment winner, it is best to remove the Sixpack experiment code from your codebase to avoid unnecessary http requests.

CORS
====

Cross-origin resource sharing can be adjusted with the following config attributes::

    cors_origin: *
    cors_headers: ...
    cors_credentials: true
    cors_methods: GET
    cors_expose_headers: ...



Contributing
============

1. Fork it
2. Start Sixpack in development mode with::

      $ PYTHONPATH=. SIXPACK_CONFIG=<path to config.yml> bin/sixpack

   and::

      $ PYTHONPATH=. SIXPACK_CONFIG=<path to config.yml> bin/sixpack-web

   We've also included a small script that will seed Sixpack with lots of random data for testing and development on sixpack-web. You can seed Sixpack with the following command::

      $ PYTHONPATH=. SIXPACK_CONFIG=<path to config.yml> sixpack/test/seed

   This command will make a few dozen requests to the ``participate`` and ``convert`` endpoints. Feel free to run it multiple times to get additional data.

   **Note:** By default the server runs in production mode. If you'd like to turn on Flask and Werkzeug debug modes set the ``SIXPACK_DEBUG`` environment variable to ``true``.

3. Create your feature branch (``git checkout -b my-new-feature``)
4. Write tests
5. Run tests with ``nosetests``
6. Commit your changes (``git commit -am 'Added some feature'``)
7. Push to the branch (``git push origin my-new-feature``)
8. Create new pull request

Please avoid changing versions numbers; we'll take care of that for you.

Using Sixpack in production?
============================

If you're a company using Sixpack in production, kindly let us know! We're going to add a 'using Sixpack' section to the project landing page, and we'd like to include you. Drop Jack a line at jack [at] seatgeek dot.com with your company name.

License
=======

Sixpack is released under the `BSD 2-Clause License`_.


.. _gunicorn: https://github.com/benoitc/gunicorn
.. _CLIENTSPEC: https://github.com/seatgeek/sixpack/blob/master/CLIENTSPEC.md
.. _HERE: https://github.com/facebook/planout/blob/master/python/planout/ops/random.py
.. _`BSD 2-Clause License`: http://opensource.org/licenses/BSD-2-Clause
