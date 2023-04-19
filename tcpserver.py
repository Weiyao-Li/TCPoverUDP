import sys
import socket
import logging

logging.basicConfig(filename='server_error.log', level=logging.ERROR)

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

def main(file_name, listening_port, ack_ip, ack_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', listening_port))

    # Buffer to store received data
    recv_buffer = dict()
    expected_seq_num = 0

    # Three-way handshake
    handshake_done = False
    while not handshake_done:
        handshake_data, addr = sock.recvfrom(1024)
        if handshake_data == expected_seq_num.to_bytes(4, byteorder='little') + b'SYN':
            # Send SYN-ACK
            sock.sendto(expected_seq_num.to_bytes(4, byteorder='little') + b'SYN-ACK', (ack_ip, ack_port))
            try:
                sock.settimeout(1)
                ack_data, addr = sock.recvfrom(1024)
                if ack_data == (expected_seq_num + 4).to_bytes(4, byteorder='little') + b'ACK':
                    handshake_done = True
            except socket.timeout:
                logging.error("Timeout occurred during three-way handshake")
                pass

    with open(file_name, 'wb') as f:
        while True:
            data, addr = sock.recvfrom(1024)
            seq_num = int.from_bytes(data[:4], byteorder='little')

            received_checksum = int.from_bytes(data[4:6], byteorder='big')
            computed_checksum = calculate_checksum(b'', data[6:])

            if received_checksum == computed_checksum and data[6:] == b'FIN':
                expected_seq_num += 4
                sock.sendto(expected_seq_num.to_bytes(4, byteorder='little'), (ack_ip, ack_port))
                break

            if seq_num == expected_seq_num and received_checksum == computed_checksum:
                recv_buffer[seq_num] = data[6:]
                expected_seq_num += len(data) - 6
                sock.sendto(expected_seq_num.to_bytes(4, byteorder='little'), (ack_ip, ack_port))

            f.seek(seq_num)
            f.write(recv_buffer[seq_num])

    sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python tcpserver.py file.txt listening_port ack_ip ack_port")
    else:
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
