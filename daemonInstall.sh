#!/bin/bash
git clone https://github.com/rellikhsu/udp-portcheck.git
chmod 755 udp-portcheck/tcp_udp_checker.py
chown root:root udp-portcheck/tcp_udp_checker.py
cp  udp-portcheck/tcp_udp_checker.py /usr/local/bin/
cp udp-portcheck/tcp_udp_checker.service /etc/systemd/system/tcp_udp_checker.service
systemctl enable tcp_udp_checker.service
systemctl daemon-reload
systemctl restart tcp_udp_checker.service
