import sys
import socket
from struct import pack, unpack

# Constants
HEADER_SIZE = 20
MSS = 576


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


def parse_packet(packet):
    _, _, seq_number, _, _, data_length, _, _ = unpack('!HHIIHHHH', packet[:HEADER_SIZE])
    data = packet[HEADER_SIZE:HEADER_SIZE + data_length]
    return seq_number, data


def make_acknowledgement(ack_number, syn_flag, fin_flag, ack_flag):
    flags = (syn_flag << 1) + fin_flag + (ack_flag << 4)
    packet = pack('!HHIIHHHH', 0, 0, 0, ack_number, (5 << 12) + flags, 0, 0, 0)
    checksum = calculate_checksum(packet)
    packet = pack('!HHIIHHHH', 0, 0, 0, ack_number, (5 << 12) + flags, 0, checksum, 0)
    return packet


# main
def main():
    if len(sys.argv) != 5:
        print("Usage: tcpserver.py <file.txt> <listening_port> <address_for_acks> <port_for_acks>")
        exit(1)

    filename, listening_port, ack_address, ack_port = sys.argv[1:]
    listening_port = int(listening_port)
    ack_port = int(ack_port)

    # Initialize socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', listening_port))

    # Perform three-way handshake
    syn_packet, sender_address = sock.recvfrom(HEADER_SIZE)
    syn_seq_number, _ = parse_packet(syn_packet)
    ack_packet = make_acknowledgement(syn_seq_number, 1, 0, 1)
    sock.sendto(ack_packet, (ack_address, ack_port))

    # Receive file.txt data
    received_data = {}
    expected_seq_number = syn_seq_number + 1
    fin_received = False
    last_ack_number = -1
    duplicate_ack_count = 0

    with open(filename, 'wb') as file:
        while not fin_received:
            data_packet, _ = sock.recvfrom(HEADER_SIZE + MSS)
            seq_number, data = parse_packet(data_packet)

            if seq_number == expected_seq_number:
                received_data[seq_number] = data
                expected_seq_number += len(data)
                while expected_seq_number in received_data:
                    file.write(received_data.pop(expected_seq_number))
                    expected_seq_number += len(data)
            elif seq_number > expected_seq_number:
                received_data[seq_number] = data

            ack_packet = make_acknowledgement(expected_seq_number - 1, 0, 0, 1)
            sock.sendto(ack_packet, (ack_address, ack_port))

            # Check for FIN flag
            _, _, _, _, flags, _, _, _ = unpack('!HHIIHHHH', data_packet[:HEADER_SIZE])
            fin_received = bool(flags & 0x01)

    # Close the socket
    sock.close()


if __name__ == '__main__':
    main()
