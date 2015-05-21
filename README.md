SingleSocket
============

Description
-----------

Python module for unidirectional socket communication, from server to client, 
for only one concurrent client.


Install
-------

    $ python setup.py install


Usage
-----

    from SingleSocket.Output import Output

    # Starts
    stream = Output(host='localhost', port=9999, web=False)
    stream.start()

    # Checks that port is available
    if not stream.port:

        # Sends a message
        stream.send('Hello peer!!')

        # Stops
        stream.stop()


Author
------

Jaume Mila <jaume@westial.com>