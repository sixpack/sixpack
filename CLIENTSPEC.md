# Client Spec

Building a Sixpack Client is straightforward, but there are some basic standards we followed internally to make implementing Sixpack easier.

## Clients...

* are responsible for generating and storing (in a cookie, session, MySQL, Redis, etc) unique client ids for each user
    * all SeatGeek clients use UUIDs, but MD5, SHA1, or anything relatively unique will work
* should accept a client id as a input for all methods (or an instance of an object)
* should accept IP addresses and user agents and pass them to Sixpack to avoid bots from participating in tests (where applicable)
    * `user_agent` and `ip_address` are the accepted query string arguments in sixpack-server
* should have a consistant interface
    * helper methods that make using sixpack easy to use in a templating language
    * convert and participate methods
* should gracefully handle server errors and responses
   * the participate method should return the `control` when Sixpack is unreachable or the server times out
* should have a short timeout on the web requests
    * internally we've settled on 250ms, though this may change
* valid alternative and experiment names as valid strings
    * this is the current regex we're using `^[a-z0-9][a-z0-9\-_ ]*$`.  It's also enforced on the server.
* should be reasonably tested
* should allow for the location of the sixpack server to be easily defined and changed
    * the prefered method is to take a single string, e.g. `http://localhost:8129`
* should assume the first argument in the list of alternatives is handled internally as the `control`