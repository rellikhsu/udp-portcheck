# udp-portcheck
Just a UDP port checking script ,but instead of service status , this python script opens a correlated TCP port for health check!
If your service opened a udp port 500, the script will continusly reflect a tcp port 500 as well. When your udp port is down ,the tcp port will goes down either.
