import sys
import socket
import time
import logging

logging.basicConfig(filename='client_error.log', level=logging.ERROR)

def calculate_checksum(header, data):
    data_size = len(data)
    if data_size % 2:
        data += b'\x00'

    checksum = 0
    for i in range(0, data_size, 2):
        checksum += (data[i] << 8) + data[i+1]

    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    return (~checksum) & 0xffff

def main(file_name, emulator_ip, emulator_port, window_size, ack_port):
    with open(file_name, 'rb') as f:
        data = f.read()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', ack_port))

    seq_num = 0
    ack_num = 0
    total_data_size = len(data)

    fin_sent = False
    fin_attempts = 0
    max_fin_attempts = 5

    # Three-way handshake
    handshake_done = False
    while not handshake_done:
        # Send SYN packet
        sock.sendto(seq_num.to_bytes(4, byteorder='little') + b'SYN', (emulator_ip, emulator_port))
        try:
            sock.settimeout(1)
            ack_data, addr = sock.recvfrom(1024)
            if ack_data == seq_num.to_bytes(4, byteorder='little') + b'SYN-ACK':
                # Send ACK for SYN-ACK
                sock.sendto((seq_num + 4).to_bytes(4, byteorder='little') + b'ACK', (emulator_ip, emulator_port))
                handshake_done = True
        except socket.timeout:
            logging.error("Timeout occurred during three-way handshake")
            pass

    while True:
        while seq_num < ack_num + window_size and seq_num < total_data_size:
            packet = seq_num.to_bytes(4, byteorder='little') + (calculate_checksum(b'', data[seq_num:seq_num + 1016])).to_bytes(2, byteorder='big') + data[seq_num:seq_num + 1016]
            sock.sendto(packet, (emulator_ip, emulator_port))
            seq_num += len(packet) - 6

        try:
            sock.settimeout(0.5)
            ack_data, addr = sock.recvfrom(1024)
            ack_num_received = int.from_bytes(ack_data, byteorder='little')
            if ack_num_received > ack_num:
                ack_num = ack_num_received
        except socket.timeout:
            logging.error("Timeout occurred while waiting for ACK")
            pass

        if not fin_sent and ack_num == total_data_size:
            if fin_attempts < max_fin_attempts:
                sock.sendto(seq_num.to_bytes(4, byteorder='little') + (calculate_checksum(b'', b'FIN')).to_bytes(2, byteorder='big') + b'FIN', (emulator_ip, emulator_port))
                fin_attempts += 1
            else:
                logging.error("Failed to send FIN packet after {} attempts, exiting.".format(max_fin_attempts))
                print("Failed to send FIN packet after {} attempts, exiting.".format(max_fin_attempts))
                break

        if ack_num == total_data_size + 4:
            break

    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python tcpclient.py file.txt emulator_ip emulator_port window_size ack_port")
    else:
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))