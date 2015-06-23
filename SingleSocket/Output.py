#!usr/bin/env python
"""Output messaging handled by socket for one concurrent client only.

Usage:
    ```
    # Starts
    stream = Output(host='localhost', port=9999, web=False)
    stream.start()

    # Checks that port is available
    if stream.running:

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


class Output(object):
    """
    SingleSocket output class.
    """

    MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    HANDSHAKE_HEAD = "HTTP/1.1 101 Switching Protocols\r\n" \
                     "Upgrade: websocket\r\n" \
                     "Connection: Upgrade\r\n" \
                     "Sec-WebSocket-Accept: {hash}\r\n" \
                     "\r\n"

    def __init__(self, host, port, web=False, max_clients=None, password=None,
                 welcome=''):
        """
        Constructor

        :param host: str. Host connected from. Set to '0.0.0.0' to allow all.
        :param port: int. Port connected to.
        :param web: bool. Flag for a websocket connection.
        :param max_clients: bool. 0 or None for unlimited.
        :param password: str. If set is used for logging in clients.
        :param welcome: str. Message sent when a client is connected.
        :return: void
        """
        self._max_clients = max_clients
        self._new_clients = Queue()
        self._clients = Queue()

        self._password = password

        self._released = threading.Event()
        self._running = threading.Event()

        self._host = host
        self._port = port

        self._web = web
        self._welcome = welcome

        self._server = None
        self._messages = Queue()

        self._emitter = None
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
        Nice stop

        :return: void
        """
        try:
            self._server.shutdown(socket.SHUT_RDWR)
            self._server.close()

        except socket.error:
            print "[!] Closing when server is not running"

        self._kill_emitter()

        self._runtime.join()

        print "[*] Stopped communication"

    def start(self, timeout=60):
        """
        Starts communication threads and returns the used port. Waits until the
        appropriate thread sets the connected event. After the set timeout
        seconds, if client is not connected, continues.

        :param timeout: int.
        :return: void
        """
        self._runtime = threading.Thread(target=self._listen)

        self._runtime.start()

        self._released.wait(timeout)

        return self._port

    def send(self, message):
        """
        Puts a message into the messages queue to be sent immediately.

        :param message: str
        :return: bool
        """

        if self._web and len(message) > 125:

            self._messages.put(message[:125])
            return self.send(message[125:])

        self._messages.put(message)

        pass

    @property
    def running(self):
        """
        Returns True if socket is working. Main flag to know the status.

        :return: bool
        """
        return self._running.is_set()

    def _listen(self):
        """
        Starts listening asynchronously

        :return: void
        """

        if not self._start_server():

            print "[x] Port in use: {:d}".format(self._port)

            self._released.set()

            return

        while self._running:
            try:
                client, address = self._server.accept()

                print "[*] Accepted from: {!s}:{:d}".format(address[0],
                                                            address[1])

            except socket.error:
                print '[x] Socket error accepting'

                self._running.clear()

                return

            if self._reaches_max_clients():
                self._clients.get()

            self._released.set()

            self._new_clients.put(client)

            if self._welcome:
                self.send(self._welcome)

            self._emitter = threading.Thread(target=self._talk)
            self._emitter.start()

        return

    def _reaches_max_clients(self):
        """
        Checks if connection reaches the max clients limit.
        If max clients is 0 or unset, clients number is unlimited.

        :return: bool
        """
        result = self._max_clients \
                 and self._clients.qsize() >= self._max_clients

        return result

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

        self._running.set()

        self._server.listen(1)

        print '[*] Listening on {!s}:{:d}'.format(self._host, self._port)

        return True

    def _kill_emitter(self):
        """
        Given the threat for client handling, nicely closes the thread and
        the client types.

        :return: void
        """
        if self._released.is_set():
            self._released.clear()
            self._emitter.join()

            print '[*] Emitter killed'

        else:
            print '[!] No emitter to kill'

        pass

    def _handshake(self, headers, client):
        """
        Given the headers and the types resource, does a handshake only on
        websocket communication.

        :param headers: dict<str>
        :return: void
        """
        for key, value in headers.iteritems():
            print key, ':', value

        socket_key = headers['Sec-WebSocket-Key']

        magic = self._hash_magic(socket_key=socket_key)

        response = self.HANDSHAKE_HEAD.format(hash=magic)

        client.send(response)

        print "[*] Handshake response:\n\t{!s}".format(response)

    def _send(self, msg):
        """
        Given a message sends to all connected clients
        :param msg: mixed
        :return: void
        """
        clients = list(self._clients.queue)

        while len(clients):
            client = clients.pop(0)
            client.send(msg)

        return

    def _login_all(self):
        """
        In case of normal socket receives the client key pass.

        In case of websocket receives the data for handshake, does the
        appropriate handshake and after receives the key pass.

        Accepts only valid new clients moving them to logged in clients.
        Only logged in clients receive the output messages.

        :return: void
        """
        if self._new_clients.empty():
            return

        client = self._new_clients.get()

        data = self._receive_hello(client=client)

        if self._web:

            print "[*] Websocket protocol is enabled"

            headers = self._parse_headers(data)

            self._handshake(headers=headers, client=client)

            data = self._receive_hello(client=client)

        if self._login(data):
            self._clients.put(client)

        else:
            client.send('Authorized only')
            client.close()

        self._login_all()

    def _receive_hello(self, client):
        """
        If password is expected and/or working on websocket mode pauses client
        to receive data from new client.

        :return: str|None
        """
        if not self._password:
            return None

        hello = client.recv(1024)

        print "[*] Received: " + hello

        return hello

    def _login(self, key_pass):
        """
        Given a key pass returns True if matches with the context password.
        Returns False if does not match.

        :param key_pass: str
        :return: bool
        """
        if not self._password:
            return True

        elif self._password == key_pass:
            return True

        else:
            return False

    def _talk(self):
        """
        - Receives the input from the new client.
        - Log in the new clients.
        - Maintains the communication meanwhile the connection with the client
        is alive.

        :return: void
        """

        self._login_all()

        while self._released.is_set():

            self._send_message()

        self._close_all()

    def _close_all(self):
        """
        Closes all clients and dequeues clients container
        :return: void
        """
        if self._clients.empty():
            return

        client = self._clients.get()
        client.send('Connection closed')
        client.close()

        self._close_all()

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
            self._send(message)

            print "[*] Message sent:\n\t{!s}".format(first)

        except socket.error, exc:

            print("[x] Error sending to a client. {!s}".format(exc.message))

        self._send_message()

    @classmethod
    def _hash_magic(cls, socket_key):
        """
        Given the types key returns a new hash composed by the key
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
