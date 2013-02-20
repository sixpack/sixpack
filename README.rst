=======
Sixpack
=======

.. image:: https://travis-ci.org/seatgeek/sixpack.png?branch=master
        :target: https://travis-ci.org/seatgeek/sixpack

Sixpack is a framework to enable A/B testing across multiple programming languages. It does this by exposing a simple API for client libraries.  Client libraries can be written in virtually any language.

Sixpack has two main parts. The first, **Sixpack-server**, is responsible for responding to web requests.  The second, **Sixpack-web**, is a web dashboard for tracking and acting on your A/B tests.  Sixpack-web is optional.

Requirements
============

* Redis
* Python >= 2.7 (3.0 untested, pull requests welcome)

Getting Started
===============

To get going, create (or don't, but you really should) a new virtualenv for your sixpack installation. Follow that up with ``pip install``::

    $ pip install sixpack

Next, create a Sixpack configuration. Here's the default::

    redis_port: 6379                        # Redis port
    redis_host: localhost                   # Redis host
    redis_prefix: sixpack                   # all Redis keys will be prefixed with this
    redis_db: 15                            # DB number in redis

    full_response: True                     # Not In Use
    disable_whiplash: True                  # Disable the whiplash/multi-armed bandit choice Algorithm

    # The regex to match for robots
    robot_regex: $^|trivial|facebook|MetaURI|butterfly|google|amazon|goldfire|sleuth|xenu|msnbot|SiteUptime|Slurp|WordPress|ZIBB|ZyBorg|pingdom|bot|yahoo|slurp|java|fetch|spider|url|crawl|oneriot|abby|commentreader|twiceler
    ignored_ip_addresses: []                # List of IP
    control_on_db_failure: True             # Not in use
    allow_multiple_experiments: False       # Not in Use

    secret_key: '<your secret key here>'    # Random key (any string is valid, required for sixpack-web to run)

You can store this file anywhere (we recommend ``/etc/sixpack/config.yml``). As long as Redis is running, you can now start the Sixpack servers like this::

    $ PYTHONPATH=. SIXPACK_CONFIG=<path to config.yml> sixpack

and::

    $ PYTHONPATH=. SIXPACK_CONFIG=<path to config.yml> sixpack-web

Sixpack-server and Sixpack-web will be listening on ports 5000 and 5001, respectively. For use in a production environment, please see the "Production Notes" section below.

We've also included a small script that will seed Sixpack with lots of random data for testing and development on sixpack-web. You can seed Sixpack with the following command::

    $ SIXPACK_CONFIG=<path to config.yml> sixpack-seed

This command will make a few dozen requests to the ``participate`` and ``convert`` endpoints. Feel free to run it multiple times to get additional data.

Using the API
=============

All interaction with Sixpack is done via ``HTTP GET`` requests. Sixpack allows for cross-language testing by accepting a unique ``client_id`` (which the client is responsible for generating) that links a participation to a conversion. All requests to Sixpack require a ``client_id``.

Participating in an Experiment
------------------------------

You can participate in an experiment with a ``GET`` request to the ``participate`` endpoint::

    $ curl http://localhost:5000/participate?experiment=button_color&alternatives=red&alternatives=blue&alternatives=orange&client_id=12345678-1234-5678-1234-567812345678

If the test does not exist, it will be created automatically.  You do not need to create the test in Sixpack-web.

Arguments
---------

``experiment`` (required) is the name of the test. Valid experiment names must be alphanumeric and can contain ``_`` and ``-``.

``alternatives`` (required) are the potential responses from Sixpack.  One of them will be the bucket that the ``client_id`` is assigned to.

``client_id`` (required) is the unique id for the user participating in the test.

``user_agent`` (optional) user agent of the user making a request. Used for bot detection.

``ip_address`` (optional) ip address of user making a request. Used for bot detection.

``force`` (optional) force a specific alternative to be returned, example::

    $ curl http://localhost:5000/participate?experiment=button_color&alternatives=red&alternatives=blue&force=red&client_id=12345678-1234-5678-1234-567812345678

In this example, red will always be returned. This is used for testing only.

Response
--------

A typical Sixpack participation response will look something like this::

    {
        status: "ok",
        alternative: {
            name: "red"
        },
        experiment: {
            version: 0,
            name: "button_color"
        },
        client_id: "12345678-1234-5678-1234-567812345678"
    }

The most interesting part of this is ``alternative``. This is a representation of the alternative that was chosen for the test and assigned to a ``client_id``. All subsequent requests to this experiment/client_id combination will be returned the same alternative.

Converting a user
-----------------

You can convert a use with a ``GET`` request to the ``convert`` endpoint::

    $ curl http://localhost:5000/convert?experiment=button_color&client_id=12345678-1234-5678-1234-567812345678

Arguments
---------

``experiment`` (required) the name of the experiment you would like to convert on

``client_id`` (request) the client you would like to convert.

Notes
-----

You'll notice that the ``convert`` endpoint does not take a ``alternative`` query parameter. This is because Sixpack handles that internally with the ``client_id``.

We've included a 'health-check' endpoint, available at ``/_status``. This is helpful for monitoring and alerting if the Sixpack service becomes unavailable.

Clients
=======

We've already provided clients in four languages. We'd love to add clients in additional languages.  If you feel inclined to create one, please first read the CLIENTSPEC_.  After writing your client, please update and pull request this file so we know about it.

- Ruby_
- Python_
- JavaScript_
- PHP_

.. _Ruby: http://github.com/seatgeek/sixpack-rb
.. _Python: http://github.com/seatgeek/sixpack-py
.. _JavaScript: http://github.com/seatgeek/sixpack-js
.. _PHP: http://github.com/seatgeek/sixpack-php

Production Notes
================

We recommend running Sixpack on gunicorn_ in production. You will need to install gunicorn in your virtual environment before running the following.

To run the sixpack server using gunicorn/gevent (a separate installation) you can run the following::

    gunicorn --access-logfile - -w 8 --worker-class=gevent sixpack.server:start

To run the sixpack web dashboard using gunicorn/gevent (a separate installation) you can run the following::

    gunicorn --access-logfile - -w 2 --worker-class=gevent sixpack.web:start

Contributing
============

1. Fork it
2. Start Sixpack in development mode with

::

    $ PYTHONPATH=. SIXPACK_CONFIG=config.yml bin/sixpack

and

::

    $ PYTHONPATH=. SIXPACK_CONFIG=config.yml bin/sixpack-web

2. Create your feature branch (``git checkout -b my-new-feature``)
3. Write tests
4. Commit your changes (``git commit -am 'Added some feature'``)
5. Push to the branch (``git push origin my-new-feature``)
6. Create new pull request

Please avoid changing versions numbers; we'll take care of that for you

Sixpack has a `Google Group`_ for support and discussion.

License
============

Sixpack is released under the `BSD 3-Clause License`_.


.. _gunicorn: https://github.com/benoitc/gunicorn
.. _CLIENTSPEC: https://github.com/seatgeek/sixpack/blob/master/CLIENTSPEC.md
.. _`BSD 3-Clause License`: http://opensource.org/licenses/BSD-3-Clause
.. _`Google Group`: https://groups.google.com/forum/?fromgroups#!forum/sixpack-ab