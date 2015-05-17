"""Usage example of a SingleSocket talking with only one html client by
websocket.

What it does:

    * Starts socket server and opens a websocket client on server waiting for
      a client.
    * When client connects, the server side client sends some messages.
    * If another client opens a communication the first client will be
      disconnected.

Requirements:

    * An html5 compatible browser with enabled websocket feature.
    * Python 2.7.x

Run the example:

    * Start the usingWebSocket.py script: `python usingWebSocket.py`
    * Open the usingWebSocketClient.html in your browser
"""

import sys
sys.path.append('..')

import time
from SingleSocket import SingleSocket

SOCKET_PORT = 9999
SOCKET_HOST = '127.0.0.1'

stream = SingleSocket(host=SOCKET_HOST, port=SOCKET_PORT, web=True)
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