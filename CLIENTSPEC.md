# Sixpack Clients

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 1. Purpose

Building a sixpack client is straightforward, but there are basic standards we've followed so far in our clients to make implementing sixpack tests consistent across languages.

## 2. Experiment interface

Clients MUST implement a "participate" method which takes two arguments, the experiment name and an ordered list of alternatives, and returns&mdash;or provides asynchronously&mdash;a string with the name of the chosen alternative. Clients MUST treat the first element of the alternatives list as the experiment's control. Clients MUST return the control alternative whenever there is an error communicating with the sixpack server (500-level error, timeout, connection error, etc.). Clients MAY alias this method to "test." Clients MAY consider implementing or extending "participate" with additional, idiomatic functionality, such as providing a block syntax in ruby, an async, callback-based syntax in javascript, or a context manager interface in python.

Clients MUST implement a "convert" method which takes one argument, the experiment name. Clients MUST NOT accept the alternative name. The sixpack server is aware of which alternative a particular client was assigned.

Clients MUST validate the format of experiment and alternative names. Currently, valid experiment/alternative names are ones that match the following regex: `^[a-z0-9][a-z0-9\-_ ]*$`. This is enforced in the sixpack server, but duplicating this functionality in the client gives developers immediate feedback when creating tests.

## 3. Users and sessions

Clients are responsible for managing user identities in a coordinated way that maintains those identities across different services/applications.

Sixpack was designed for use primarily in a web context. On the web the most basic and pervasive method of client-side storage is the cookie. It's RECOMMENDED that clients use cookies to share state between each other. A common flow might look like:

* User visits a page on seatgeek.com
* The PHP sixpack client notices that the user has no user token, creates one and stores it in a cookie named "sixpack" on the seatgeek.com domain
* The user navigates to a page which uses the JS client to start a test
* Before creating a user token, the JS client first checks for a sixpack cookie, which it finds and uses
* The user makes a purchase which involves POSTing to a python web service on the seatgeek.com domain
* The python sixpack client reads the user token from the cookie and uses it in its "convert" call

This limits sixpack's cross-language capability to services on the same domain, so it may be worth considering other ways of sharing state. One solution might be a "\_sixpack" query string parameter, but that is beyond the scope of this spec.

Clients SHOULD attempt to make the process of sharing user tokens between clients as seamless and hands-free as possible. For example a PHP client might automatically read and write the user token using the $\_COOKIES global.

Clients SHOULD forward to the server the ip address and user agent of the user where possible. This allows the server to prevent the application developers and obvious bots from participating in tests and diluting or skewing test results. Note: a list of developer ips and a regular expression to match bot user agents can be provided in the sixpack server config.

It's RECOMMENDED that clients expose the concept of a user "Session" in a way that allows advanced users to instantiate and manipulate it directly. Instantiating a Session SHOULD allow for specifying a user's ip address, user agent and user token.

Clients SHOULD be able to return a "forced" alternative via query string to aid in testing web development and viewing alternatives without effecting conversion rates. The client SHOULD use the pattern of `?sixpack-force-EXPERIMENT-NAME=ALTERNATIVE`

## 4. Performance considerations

Sixpack clients run the risk of negatively impacting the performance of the application that is being tested. In order to minimize this risk, sixpack clients SHOULD use short timeouts when connecting to the server. Clients SHOULD also consider the use of HTTP Keep-Alive and HTTP connection pooling.

## 5. Additional considerations

Clients MUST allow the location of the sixpack server to be specified with a single argument, e.g. `http://my.sixpack.host:8129/sixpack/mount/point`.
