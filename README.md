Sixpack
=======

Sixpack is a language-agnostic A/B testing framework under active development at [SeatGeek](http://seatgeek.com/)..

Travis
======

[![Build Status](https://travis-ci.org/seatgeek/sixpack.png)](https://travis-ci.org/seatgeek/sixpack)

Notes
=====

gunicorn --access-logfile - -w 8 --worker-class=gevent server:start

Starting Sixpack (Developement)
===============================

$ cd sixpack
(virtualenv here, if you want)
$ pip install -r requirements.txt
$ cd sixpack
$ python server.py

server will be on localhost:5000

To seed some random data
$ python seed.py (with above server running)

Starting Sixpack-Web (Development)
==================================

$ cd sixpack
$ python sixpack-web.py

server will be on localhost:5001

