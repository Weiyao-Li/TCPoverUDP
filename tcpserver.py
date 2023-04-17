import sys
import socket


def main(output_file, listen_port, emulator_ip, emulator_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the listening port
    sock.bind(('', listen_port))

    # Initialize the expected sequence number and the data buffer
    expected_seq_num = 0
    data_buffer = bytearray()

    # Main loop
    while True:
        packet, addr = sock.recvfrom(1024)
        seq_num = int.from_bytes(packet[:4], byteorder='little')

        # Check if this is a FIN packet
        if packet[4:] == b'FIN':
            if seq_num == expected_seq_num:
                # Acknowledge the FIN packet
                sock.sendto(expected_seq_num.to_bytes(4, byteorder='little'), (emulator_ip, emulator_port))
                break
            else:
                # Discard the FIN packet and continue
                continue

        # Check if the packet's sequence number matches the expected sequence number
        if seq_num == expected_seq_num:
            # Add the data from the packet to the data buffer
            data_buffer.extend(packet[4:])
            expected_seq_num += len(packet) - 4

        # Send an ACK with the expected sequence number
        sock.sendto(expected_seq_num.to_bytes(4, byteorder='little'), (emulator_ip, emulator_port))

    # Write the received data to the output file
    with open(output_file, 'wb') as f:
        f.write(data_buffer)

    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python tcpserver.py output_file listen_port emulator_ip emulator_port")
    else:
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
