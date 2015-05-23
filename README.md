SingleSocket
============

Description
-----------

Python module for unidirectional socket communication, from server to client.
 
Only one exclusive listening client. If other client connects to the same
socket the first client will be disconnected.


Install
-------

    $ python setup.py install


Usage
-----

    from SingleSocket.Output import Output

    # Configures attributes
    stream = Output(host='localhost', port=9999, web=False)
    
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