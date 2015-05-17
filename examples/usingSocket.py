"""Usage example of a SingleSocket talking with only one socket client.

What it does:

    * Starts socket server and opens a socket client on server waiting for
      a client.
    * When client connects, the server side client sends some messages.
    * If another client opens a communication the first client will be
      disconnected.

Requirements:

    * Python 2.7.x

Run the example:

    * Start the usingSocket.py script: `python usingSocket.py`
    * Open a shell and connect the netcat client: `nc 127.0.0.1 9999`
"""

import sys
sys.path.append('..')

import time
from SingleSocket import SingleSocket

SOCKET_PORT = 9999
SOCKET_HOST = '127.0.0.1'

stream = SingleSocket(host=SOCKET_HOST, port=SOCKET_PORT, web=False)
stream.start()

if not stream.port_in_use:
    # Waiting while you are opening the client
    time.sleep(10)

    stream.send("Hello World!")
    time.sleep(1)

    stream.send("Hello Moon!")
    time.sleep(1)

    stream.send("Hello Mars!")
    time.sleep(1)

    stream.send("Hello Juneda!")
    time.sleep(1)

    stream.stop()