SingleSocket
============

Description
-----------

Python module for unidirectional socket communication, from server to client.
 
Output socket for limited and unlimited concurrent clients.

When is configured to accept only one exclusive listening client, if other 
client connects to the same socket, the first client is disconnected.

Provided an optional key pass authorization validating the client who knows
the password. Still not supported on websocket protocol mode.

Optionally you can connect a javascript application by the websocket protocol.


Install
-------

    $ python setup.py install


Usage
-----
    from SingleSocket.Output import Output

    # Configures attributes
    stream = Output(
        host='localhost',           # Accepted clients on localhost only
        port=9999,                  # Socket port
        web=True,                   # Websocket protocol mode
        max_clients=2,              # 3rd client connects other is disconnected
        password='1234',            # Only clients providing password
        welcome='bla bla')          # Client receives this message on logging in
    
    # Creates the socket server and connects the emitter with the listener.
    # This method waits until the first client connects or the timeout expires.
    port = stream.start()

    # Checks if socket is working.
    if not stream.running:
        exit(0)

    # Sends a message
    stream.send('Hello peer!!')

    # Nicely stops
    stream.stop()


Author
------

Jaume Mila <jaume@westial.com>