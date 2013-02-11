Sixpack
=======

.. image:: https://travis-ci.org/seatgeek/sixpack.png?branch=master
        :target: https://travis-ci.org/seatgeek/sixpack

Sixpack is a tool to help solve the problem of A/B testing across multiple programming languages. It does this by exposing a very simple API that a client library in virtually any language can make requests against.


Requirements
============

* Redis
* Python >= 2.7 (3.0 Untested, Pull Requests welcome)

Running the Services
====================

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
    SIXPACK_CONFIG=config.yml bin/sixpack

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
    SIXPACK_CONFIG=config.yml bin/sixpack-web


The sixpack web dashboard will be accessible at ``localhost:5001``

