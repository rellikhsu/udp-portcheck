#!/usr/bin/python3
import logging
import socket
import subprocess
import threading
import time
import re

# 設置日誌配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 全局字典，用於監控 UDP 端口狀態
udp_ports_status = {500: False, 4500: False}
# 用於存儲 TCP 伺服器 sockets 的字典
tcp_server_sockets = {}

def check_udp_port(port):
    """檢查 UDP 端口是否開放。"""
    try:
        output = subprocess.run(['netstat', '-anu'], capture_output=True, text=True).stdout
        return re.search(rf":{port}\s", output) is not None
    except subprocess.CalledProcessError as e:
        logging.error(f"執行 netstat 時出錯: {e}")
        return False

def tcp_server(port):
    """開啟或關閉對應的 TCP 伺服器，反映 UDP 端口的狀態。"""
    server_socket = None
    while True:
        time.sleep(1)  # 每秒檢查一次 UDP 端口狀態
        if udp_ports_status[port]:  # 如果 UDP 端口開啟，則啟動 TCP 伺服器
            if not server_socket:
                # 創建並存儲 socket 實例
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind(('', port))
                server_socket.listen(5)
                tcp_server_sockets[port] = server_socket
                logging.info(f"TCP 伺服器正在監聽端口 {port}。")
            else:
                # 接受連接
                try:
                    client_socket, addr = server_socket.accept()
                    logging.info(f"來自 {addr} 的連接已接受。")
                    client_socket.settimeout(10.0)  # 為連接設置超時
                    # 在這裡添加處理客戶端請求的代碼
                    # ...
                    # 處理完成後，關閉連接
                    client_socket.close()
                    logging.info(f"來自 {addr} 的連接已關閉。")
                except socket.timeout:
                    logging.warning("連接超時。")
                except Exception as e:
                    logging.exception("處理連接時發生錯誤。")
        else:  # 如果 UDP 端口關閉，則關閉 TCP 伺服器
            if server_socket:
                server_socket.close()
                logging.info(f"TCP 伺服器端口 {port} 已關閉。")
                server_socket = None
                tcp_server_sockets.pop(port, None)

def monitor_udp_ports():
    """監控 UDP 端口的狀態。"""
    global udp_ports_status
    while True:
        for port in udp_ports_status.keys():
            udp_ports_status[port] = check_udp_port(port)
        time.sleep(1)

if __name__ == '__main__':
    # 啟動 UDP 端口監控線程
    threading.Thread(target=monitor_udp_ports, daemon=True).start()

    # 為每個 UDP 端口啟動一個 TCP 伺服器監聽線程
    for port in udp_ports_status.keys():
        threading.Thread(target=tcp_server, args=(port,), daemon=True).start()

    # 主線程保持運行
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("程序被手動中止。")
        for port, server in tcp_server_sockets.items():
            server.close()

