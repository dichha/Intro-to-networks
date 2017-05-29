import select
import socket
import sys
import queue
import os
import re


def process_http_header(request_header):
	'''checking format of HTTP Request and sending response accordingly'''
	'''
	GET /cars/ford.html HTTP/1.1
	Host: 127.0.0.1:4000
	Connection: keep-alive
	Upgrade-Insecure-Requests: 1
	User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36
	Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
	DNT: 1
	Accept-Encoding: gzip, deflate, sdch, br
	Accept-Language: en-US,en;q=0.8
	'''
	'''
	:param request_header: list of http-header
	:return: uri or None
	'''


	req_header_list = request_header.splitlines()
	'''handling empty request'''
	if (len(req_header_list) == 0):
	    return None
	#print(req_header_list[0])
	first_line = req_header_list.pop(0)
	regex_header_verb = re.compile(r'GET\s{1}[A-Za-z0-9\.\/]*\s{1}HTTP\/1\.1')
	
	verb_uri_match = bool(regex_header_verb.match(first_line))

	if(verb_uri_match == False):
	    #print("wrong  format for request uri")
	    return None

	#print("First Line: ", first_line)
	(verb, uri, version) = first_line.split()
	'''if verb is not GET send an error - not supported'''
	req_header_list = req_header_list[:-1]# -1 for taking last empty item
	#print("Rest of headers value: ",req_header_list)
	regex_header_key_val = re.compile(r'\s*(?P<key>.+\S)\s*:\s+(?P<value>.*\S)\s*')
	for header in req_header_list:
	    #print(header)
	    match = bool(regex_header_key_val.match(header))
	    if match == False:
	        '''write code for bad format and send HTTP Bad Request response'''
	       	#print("bad format")
	        return None
	return uri




if __name__ == '__main__':
	'''arguments for server hostname and port'''
	arg_list = sys.argv
	hostname = arg_list[1]
	port = int(arg_list[2])
	server_address = (hostname, port)
	#print(server_address)


	#Create a TCP/IP socket
	print('creating a TCP socket')
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0) #blocking is False ==> non-blocking socket

	#Bind the socket to the port
	print('starting up on %s port %s' % server_address)
	server.bind(server_address)

	#Listen to incoming connections
	server.listen(5) #listening for upto 5 connections

	#Sockets from which we expect to read  == producer
	inputs = [server]

	#Sockets to which we expect to write == consumer
	outputs = []

	#Outgoing message queues (socket: Queue)
	content_queues = {}

	while inputs:
		#Wait for at least one of the sockets to be ready for processing
		print('\n waiting for the next event')
		readable, writeable, exceptional = select.select(inputs, outputs, inputs)

		#handle inputs
		for s in readable:
			if s is server:
				# A "readable" server is ready to accept a connection

				connection, client_address = s.accept()
				print('new connection from ', client_address)
				connection.setblocking(0) #non-blocking connection
				inputs.append(connection)

				#Give the connection a queue for data we want to send
				content_queues[connection] = queue.Queue()
			else:
				data = s.recv(1024)
				if data:
					#A readable client socket has data
					print('received %s from %s' % (data, s.getpeername()))
					data = data.decode('utf-8')
					uri = process_http_header(data)
					print("URI: ", uri)
					if(uri == None):
						'''send bad request page'''
						header = 'HTTP/1.1 400 Bad Request \r\n Content-Type: text/html\r\n\r\n'
						content_bad_req = '<html><head><title>Bad Request</title></head><body>boo! bad request :(</body></html>'
						content = header.encode('utf-8') + content_bad_req.encode('utf-8')
						content_queues[s].put(content)
						#Add output channel for response
						if s not in outputs:
							outputs.append(s)
					else:
						curr_working_dir = os.path.dirname(os.path.abspath(__file__))+'/static'
						print('working dir: ', curr_working_dir)
						uri_path = curr_working_dir + '/' + uri[1:]
						print('URI: ', uri_path)
						body = b""

						try:
							with open(uri_path, 'rb') as file:
								for line in file:
									body += line

							header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
							content = header.encode('utf-8') + body
							content_queues[s].put(content)

							#Add output channel for response
							if s not in outputs:
								outputs.append(s)
						except IOError:
							print("Cannot open file")
							header = 'HTTP/1.1 404 Not Found\r\n Content-Type:text/html\r\n\r\n'
							content_not_found = '<html><head><title>Page not found</title></head><body>The page was not found</body></html>'
							content = header.encode('utf-8') + content_not_found.encode('utf-8')
							content_queues[s].put(content)
					
							#Add output channel for response
							if s not in outputs:
								outputs.append(s)
				else:
					#interpret empty results as closed connection
					print('closing ', client_address, 'after reading no data')
					#Stop listening for input on the connection
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()

					#Remove message queue
					del content_queues[s]


		#handle outputs
		for s in writeable:
			try:
				next_content= content_queues[s].get_nowait() #equivalent to get(False)
			except queue.Empty:
				#No contents waiting so stop checking for writability
				print('output queue for ', s.getpeername(), ' is empty.')
				outputs.remove(s)
			else:
				print('sending "%s" to %s' % (next_content, s.getpeername()))
				s.send(next_content)

		#Handle "exceptional conditions"
		for s in exceptional:
			print('handling exceptional condition for ', s.getpeername())
			#stop listening for inut on the connection
			inputs.remove(s)

			if s in outputs:
				outputs.remove(s)
			s.close()

			#remove message queue
			del content_queues[s]

		


