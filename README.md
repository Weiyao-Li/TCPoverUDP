# TCPoverUDP

This project involves implementing a simplified TCP over UDP using a link emulator to simulate network impairments. The objective is to create a sender (client) and receiver (server) transport-level code with a three-way handshake, error logging, and FIN request for ending transmission. The TCP header format is implemented without options, and the checksum is calculated over the header and data. The goal is to test the implementation using the link emulator and verifying correct data transmission.

## Usage

To use this implementation, follow these steps:

1. Run the UDP link emulator with the following command:

**./newudpl -i localhost -o localhost -L 50**


*This command starts the UDP link emulator with a simulated speed of 1000 kb/s, 50% random packet loss, and other default parameters. Adjust the parameters as needed for your testing.*

<br>

2. Start the TCP server with the following command:


**python tcpserver.py received_file.txt 9000 localhost 9001**


*This command starts the TCP server listening on port `9000` for incoming connections from clients. The server saves the received data to a file named `received_file.txt` and uses port `9001` to receive acknowledgments from the client.*

<br>

3. Start the TCP client with the following command:



**python tcpclient.py file.txt 127.0.0.1 9000 512 9001**


*This command starts the TCP client and sends the contents of the file `file.txt` to the server at IP address `127.0.0.1` (i.e., localhost) on port `9000`. The client uses a window size of `512` bytes and port number `9001` to receive acknowledgments from the server.*

<br>

Adjust the file names, IP addresses, port numbers, and other parameters as needed for your testing.




