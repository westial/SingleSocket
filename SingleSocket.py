#!usr/bin/env python
"""Output handled by socket for one client only.

Returns
Websocket protocol is supported.

Usage:
    ```
    # Starts
    stream = SingleSocket(host='localhost', port=9999, web=False)
    stream.start()

    # Checks that port is available
    if not stream.port_in_use:

        # Sends a message
        stream.send('Hello peer!!')

        # Stops
        stream.stop()
    ```
"""

from Queue import Queue
import socket
import base64
import threading
from hashlib import sha1


class SingleSocket():
    """
    SingleSocket output class.
    """

    MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    HSHAKE_RESP = "HTTP/1.1 101 Switching Protocols\r\n" \
                  "Upgrade: websocket\r\n" \
                  "Connection: Upgrade\r\n" \
                  "Sec-WebSocket-Accept: {hash}\r\n" \
                  "\r\n"

    def __init__(self, host, port, web=False):
        """
        Constructor

        :param host: str
        :param port: int
        :param web: bool
        :return: void
        """
        self._client = None
        self._running = True
        self._connected = False
        self._host = host
        self._port = port
        self._web = web

        self.port_in_use = False

        self._server = None
        self._messages = Queue()

        self._listener = None
        self._runtime = None

        pass

    def reconfigure(self, host, port, web):
        """
        Recycles the object. Stopping the object before is recommended.

        :param host: str
        :param port: int
        :param web: bool
        :return: void
        """
        print "[*] Recycled object"

        return self.__init__(host=host, port=port, web=web)

    def stop(self):
        """
        Nicely stops the current communication

        :return: void
        """
        self._kill_client()

        self._running = False

        self._server.shutdown(socket.SHUT_RDWR)
        self._server.close()

        self._runtime.join()

        print "[*] Stopped communication"

    def start(self):
        """
        Starts communication

        :return: void
        """
        self._runtime = threading.Thread(target=self._async_start)

        self._runtime.start()

        pass

    def send(self, message):
        """
        Puts a message into the messages queue to be sent immediately.

        :param message: str
        :return: bool
        """
        self._messages.put(message)

        pass

    def _async_start(self):
        """
        Starts asynchronously

        :return: void
        """

        if not self._start_server():

            print "[x] Port in use: {:d}".format(self._port)

            self.port_in_use = True

        while self._running:
            try:
                client, address = self._server.accept()

            except socket.error:
                print '[*] Broken server'
                return

            if self._client:
                self._kill_client()

            self._client = client
            self._connected = True

            print "[*] Accepted connection from: {!s}:{:d}".format(address[0],
                                                                   address[1])

            self._listener = threading.Thread(target=self._talk)
            self._listener.start()

        pass

    def _start_server(self):
        """
        Starts server on first available port. Returns True if does.
        If there is no port available returns False.

        :return: bool
        """
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._server.bind((self._host, self._port))

        except socket.error:
            return False

        self._server.listen(1)

        print '[*] Listening on {!s}:{:d}'.format(self._host, self._port)

        return True

    def _kill_client(self):
        """
        Given the threat for client handling, nicely closes the thread and
        the client socket.

        :return: void
        """
        if self._connected:
            self._connected = False
            self._listener.join()

            print '[*] Client killed'

        else:
            print '[*] Client still not alive'

        pass

    def _handshake(self, headers):
        """
        Given the headers and the socket resource, does a handshake only on
        websocket communication.

        :param headers: dict<str>
        :return: void
        """
        for key, value in headers.iteritems():
            print key, ':', value

        socket_key = headers['Sec-WebSocket-Key']

        magic = self._hash_magic(socket_key=socket_key)

        response = self.HSHAKE_RESP.format(hash=magic)

        self._client.send(response)

        print "[*] Handshake response:\n\t{!s}".format(response)

    def _talk(self):
        """
        Receives the input from the new client and maintains the communication
        meanwhile the connection with the client is alive.

        :return: void
        """
        if self._web:

            data = self._client.recv(1024)

            print "[*] Received: " + data

            headers = self._parse_headers(data)

            self._handshake(headers=headers)

        while self._connected:

            self._send_message()

        self._client.close()

    def _send_message(self):
        """
        Prepares and sends all message in queue.

        :return: void
        """
        if self._messages.empty():
            return

        first = self._messages.get()

        if self._web:
            message = bytearray([0b10000001, len(first)])

            # append the data bytes
            for byte in bytearray(first):
                message.append(byte)

        else:
            message = first

        try:
            self._client.send(message)

            print "[*] Message sent:\n\t{!s}".format(first)

        except socket.error:

            print("[x] Error sending to a client")

        self._send_message()


    @property
    def port_in_use(self):
        """
        Port in use flag getter

        :return: bool
        """
        return self._port_in_use

    @port_in_use.setter
    def port_in_use(self, value):
        """
        Port in use flag setter

        :param value: bool
        :return: void
        """
        self._port_in_use = value
        pass

    @classmethod
    def _hash_magic(cls, socket_key):
        """
        Given the socket key returns a new hash composed by the key
        and the magic uuid.

        :param socket_key: str
        :return: str
        """
        output = sha1(socket_key + cls.MAGIC).digest()
        output = base64.b64encode(output)

        return output

    @classmethod
    def _parse_headers(cls, data):
        """
        Parses headers from client

        :param data: str
        :return: dict
        """
        headers = {}
        lines = data.splitlines()

        for l in lines:
            parts = l.split(": ", 1)

            if len(parts) == 2:
                headers[parts[0]] = parts[1]

        headers['get'] = lines[0]

        headers['code'] = lines[len(lines) - 1]

        return headers