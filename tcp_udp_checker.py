#!/usr/bin/python3
import threading
import socket
import subprocess
import time
import re

port_regex_template = r"udp\s+\d+\s+\d+\s+.*:{}\s"

def is_udp_port_open(port, output):
    """ Check if the specified UDP port is open """
    try:
        regex = re.compile(port_regex_template.format(port))
        return bool(regex.search(output))
    except Exception as e:
        print(f"Error in is_udp_port_open: {e}")
        return False

def get_netstat_output():
    """ Run the netstat command and return its output """
    result = subprocess.run(['netstat', '-anu'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def tcp_server(port):
    """ Start a simple server on the specified TCP port """
    while True:
        netstat_output = get_netstat_output()
        if is_udp_port_open(port, netstat_output):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    s.listen(20)
                    print(f"TCP port {port} is listening...")

                    while True:
                        conn, addr = s.accept()
                        with conn:
                            if is_udp_port_open(port, get_netstat_output()):
                                print(f"Connection from {addr}")
                                conn.sendall(b"Hello, TCP!\n")
                            else:
                                print(f"UDP port {port} closed, disconnecting TCP connection...")
                                conn.close()
                                break
                except socket.error as e:
                    print(f"Socket error: {e}")
                    break
        else:
            print(f"UDP port {port} is not available, waiting...")
            time.sleep(1)

if __name__ == "__main__":
    # Starting two TCP server threads, each monitoring a different UDP port
    threading.Thread(target=tcp_server, args=(500,), daemon=True).start()
    threading.Thread(target=tcp_server, args=(4500,), daemon=True).start()

    while True:
        time.sleep(1)

