import socket
import sys
import time

if __name__ == '__main__':
	arg_list = sys.argv
	hostname = arg_list[1]
	port = int(arg_list[2])
	server_address = (hostname, port)


	'''For Successful response'''
	requests = ['GET /index.html HTTP/1.1\r\nHost: 127.0.0.1:4000\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nDNT: 1\r\nAccept-Encoding: gzip, deflate, sdch, br\r\nAccept-Language: en-US,en;q=0.8\r\n\r\n']

	'''For Bad Request'''
	#requests = ['GEET /index.html HTTP/1.1\r\nHost: 127.0.0.1:4000\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nDNT: 1\r\nAccept-Encoding: gzip, deflate, sdch, br\r\nAccept-Language: en-US,en;q=0.8\r\n\r\n']

	'''For Page not Found'''
	#requests = ['GET /static/flower.html HTTP/1.1\r\nHost: 127.0.0.1:4000\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nDNT: 1\r\nAccept-Encoding: gzip, deflate, sdch, br\r\nAccept-Language: en-US,en;q=0.8\r\n\r\n']



	#Create a TCP/IP socket
	socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			]

	#Connect the socket to the port where the server is listening
	print('connecting to %s port %s', server_address)

	for s in socks:
		s.connect(server_address)


	for request in list(requests): #sending 1 character == 1 byte at a time
		#Send request on both sockets
		for s in socks:
			print('%s: sending "%s"' % (s.getsockname(), request))
			s.send(request.encode('utf-8'))

		#Read responses on both sockets
		for s in socks:
			data = s.recv(1024)
			print('%s: received "%s"'%(s.getsockname(), data))

			if not data:
				print('closing socket ', s.getsockname())
				s.close()