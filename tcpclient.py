import sys
import socket


def main(file_name, emulator_ip, emulator_port, window_size, ack_port):
    # Read data from the file
    with open(file_name, 'rb') as f:
        data = f.read()

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the ACK port
    sock.bind(('', ack_port))

    # Set the initial sequence number and ACK number
    seq_num = 0
    ack_num = 0

    # Calculate the total size of the data to be sent
    total_data_size = len(data)

    # Variables to control the FIN packet sending
    fin_sent = False
    fin_attempts = 0
    max_fin_attempts = 5

    # Main loop
    while True:
        # Send data while there is still data left to send and the sequence number is within the window
        while seq_num < ack_num + window_size and seq_num < total_data_size:
            # Send a packet with the sequence number and the data
            packet = seq_num.to_bytes(4, byteorder='little') + data[seq_num:seq_num + 1020]
            sock.sendto(packet, (emulator_ip, emulator_port))
            seq_num += len(packet) - 4

        # Receive ACKs
        try:
            sock.settimeout(0.5)
            ack_data, addr = sock.recvfrom(1024)
            ack_num_received = int.from_bytes(ack_data, byteorder='little')
            if ack_num_received > ack_num:
                ack_num = ack_num_received
        except socket.timeout:
            pass

        # Send FIN packet after all data has been acknowledged
        if not fin_sent and ack_num == total_data_size:
            if fin_attempts < max_fin_attempts:
                sock.sendto(seq_num.to_bytes(4, byteorder='little') + b'FIN', (emulator_ip, emulator_port))
                fin_attempts += 1
            else:
                print("Failed to send FIN packet after {} attempts, exiting.".format(max_fin_attempts))
                break

        # Exit the loop when the server acknowledges the FIN packet
        if ack_num == total_data_size + 4:
            break

    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python tcpclient.py file.txt emulator_ip emulator_port window_size ack_port")
    else:
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
