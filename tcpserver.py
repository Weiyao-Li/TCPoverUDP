import sys
import socket
from struct import unpack, pack


def main():
    if len(sys.argv) != 5:
        print("Usage: python tcpserver.py <output_file> <listening_port> <udpl_ip> <udpl_port>")
        sys.exit(1)

    output_file = sys.argv[1]
    listening_port = int(sys.argv[2])
    udpl_ip = sys.argv[3]
    udpl_port = int(sys.argv[4])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', listening_port))

    expected_seq = 0
    fin_received = False
    with open(output_file, 'wb') as f:
        while not fin_received:
            data, addr = sock.recvfrom(1024)
            if addr[0] == udpl_ip and addr[1] == udpl_port:
                seq_num, = unpack('I', data[:4])
                if seq_num == expected_seq:
                    # Check for FIN request
                    if data[4:7] == b'FIN':
                        fin_received = True
                    else:
                        f.write(data[4:])
                        expected_seq += len(data) - 4

                ack = pack('I', expected_seq)
                sock.sendto(ack, (udpl_ip, udpl_port))

    sock.close()


if __name__ == '__main__':
    main()
