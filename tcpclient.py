import sys
import socket
from struct import pack, unpack
import time
import threading

# Constants
MSS = 576
HEADER_SIZE = 20


# Helper functions
def calculate_checksum(packet):
    total_words = len(packet) // 2
    checksum = 0
    for i in range(total_words):
        word = (packet[i * 2] << 8) + packet[i * 2 + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    if len(packet) % 2:
        checksum += packet[-1] << 8
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return (~checksum) & 0xffff


def make_packet(seq_number, data, syn_flag, fin_flag, ack_flag):
    data_length = len(data)
    flags = (syn_flag << 1) + fin_flag + (ack_flag << 4)
    packet = pack('!HHIIHHHH', 0, 0, seq_number, 0, (5 << 12) + flags, data_length, 0, 0)
    packet += data
    checksum = calculate_checksum(packet)
    packet = pack('!HHIIHHHH', 0, 0, seq_number, 0, (5 << 12) + flags, data_length, checksum, 0)
    packet += data
    return packet


def parse_acknowledgement(packet):
    _, _, ack_number, _, _, _, _, _ = unpack('!HHIIHHHH', packet[:HEADER_SIZE])
    return ack_number


def receive_acks(sock, acknowledged_seq_numbers):
    while True:
        ack_packet, _ = sock.recvfrom(HEADER_SIZE)
        ack_number = parse_acknowledgement(ack_packet)
        acknowledged_seq_numbers.append(ack_number)


# main
def main():
    if len(sys.argv) != 6:
        print("Usage: tcpclient.py <file.txt> <address_of_udpl> <port_number_of_udpl> <window_size> <ack_port_number>")
        exit(1)

    filename, emulator_address, emulator_port, window_size, ack_port = sys.argv[1:]
    emulator_port = int(emulator_port)
    window_size = int(window_size)
    ack_port = int(ack_port)

    # Initialize socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', ack_port))

    # Perform three-way handshake
    handshake_packet = make_packet(0, b'', 1, 0, 0)
    sock.sendto(handshake_packet, (emulator_address, emulator_port))

    acknowledged_seq_numbers = []
    ack_receiver_thread = threading.Thread(target=receive_acks, args=(sock, acknowledged_seq_numbers))
    ack_receiver_thread.start()

    while 0 not in acknowledged_seq_numbers:
        time.sleep(0.1)

    # Send file.txt data
    with open(filename, 'rb') as file:
        data = file.read(MSS)
        seq_number = 1
        while data:
            data_packet = make_packet(seq_number, data, 0, 0, 0)
            sock.sendto(data_packet, (emulator_address, emulator_port))
            seq_number += len(data)
            data = file.read

    # Wait for all data to be acknowledged
    while seq_number not in acknowledged_seq_numbers:
        time.sleep(0.1)

    # Send FIN request
    fin_packet = make_packet(seq_number, b'', 0, 1, 0)
    sock.sendto(fin_packet, (emulator_address, emulator_port))

    # Wait for FIN ACK
    while seq_number not in acknowledged_seq_numbers:
        time.sleep(0.1)

    # Close the socket
    sock.close()
    ack_receiver_thread.join()


if __name__ == '__main__':
    main()
