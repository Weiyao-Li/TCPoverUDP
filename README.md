# TCPoverUDP

This project involves implementing a simplified TCP over UDP using a link emulator to simulate network impairments. The objective is to create a sender (client) and receiver (server) transport-level code with a three-way handshake, error logging, and FIN request for ending transmission. The TCP header format is implemented without options, and the checksum is calculated over the header and data. The goal is to test the implementation using the link emulator and verifying correct data transmission.

## Usage

To use this implementation, follow these steps:

1. Run the UDP link emulator with the following command:

**./newudpl -p 2222:3333 -i 127.0.0.1:6666 -o 127.0.0.1:5555 -vv -L50**


<br>

2. Start the TCP server with the following command:


**python tcpserver.py output.txt 5555 127.0.0.1 6666**


<br>

3. Start the TCP client with the following command:



**python tcpclient.py file.txt 127.0.0.1 2222 512 6666**



<br>

Adjust the file names, IP addresses, port numbers, and other parameters as needed for your testing.

## Submitted Files

- descrition.txt: overall program design, a verbal description of how it works, design tradeoffs considered and made
- tcpclient.py: Python code for the TCP client implementation
- tcpserver.py: Python code for the TCP server implementation
- client_error.log: Log file for client-side errors
- server_error.log: Log file for server-side errors

## Known Issues

- The program does not support multi-threading for handling multiple client requests simultaneously.
- The program does not support resuming an interrupted file transfer.


