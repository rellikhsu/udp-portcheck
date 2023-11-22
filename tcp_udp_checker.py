import threading
import socket
import subprocess
import time
import re

def is_udp_port_open(port, output):
    """ Check if the specified UDP port is open using a modified regex """
    regex = r"^udp\s.*:{}\b".format(port)
    return bool(re.search(regex, output, re.MULTILINE))

def get_netstat_output():
    """ Run the netstat command and return its output """
    result = subprocess.run(['netstat', '-anu'], stdout=subprocess.PIPE)
    return result.stdout.decode()

def tcp_server(port):
    """ Start a simple server on the specified TCP port """
    while True:
        netstat_output = get_netstat_output()
        if is_udp_port_open(port, netstat_output):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    s.listen()
                    print(f"TCP port {port} is listening...")

                    while is_udp_port_open(port, get_netstat_output()):
                        s.settimeout(1)  # Set a timeout for accepting connections
                        try:
                            conn, addr = s.accept()
                            with conn:
                                print(f"Connection from {addr}")
                                conn.sendall(b"Hello, TCP!\n")
                        except socket.timeout:
                            continue  # Continue checking if the UDP port is open
                    print(f"TCP port {port} closing...")

                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)  # Wait for a while and retry
        else:
            print(f"UDP port {port} is not available, waiting...")
            time.sleep(1)  # Wait for a while before retrying

if __name__ == "__main__":
    # Starting TCP servers for ports 500 and 4500 in separate threads
    threading.Thread(target=tcp_server, args=(500,), daemon=True).start()
    threading.Thread(target=tcp_server, args=(4500,), daemon=True).start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
