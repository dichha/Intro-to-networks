import socket
import sys
import os
import re

def process_http_header(request_header):
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
	if (len(req_header_list) == 0):
	    return None
	#print(req_header_list[0])
	first_line = req_header_list.pop(0)
	regex_header_verb = re.compile(r'GET\s{1}[A-Za-z0-9\.\/]*\s{1}HTTP\/1\.1')
	
	verb_uri_match = bool(regex_header_verb.match(first_line))

	if(verb_uri_match == False):
	    print("wrong  format for request uri")
	    return None

	print("First Line: ", first_line)
	(verb, uri, version) = first_line.split()
	'''if verb is not GET send an error - not supported'''
	req_header_list = req_header_list[:-1]# -1 for taking last empty item
	print("Rest of headers value: ",req_header_list)
	regex_header_key_val = re.compile(r'\s*(?P<key>.+\S)\s*:\s+(?P<value>.*\S)\s*')
	for header in req_header_list:
	    #print(header)
	    match = bool(regex_header_key_val.match(header))
	    if match == False:
	        '''write code for bad format and send HTTP Bad Request response'''
	        print("bad format")
	        return None
	return uri





if __name__ == '__main__':
    '''arguments for server hostname and port'''
    arg_list = sys.argv
    #print(arg_list)
    hostname = arg_list[1]
    port = int(arg_list[2])
    server_address = (hostname, port)
    #print(server_address)

    '''creating a TCP/IP socket'''
    print('creating a TCP socket')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('connecting to host %s port %s' % server_address)

    '''bind() us used to associate socket with the server_address'''
    sock.bind(server_address)

    '''listen() puts the socket into a server mode'''
    sock.listen(1) #listening for upto 5 connections

    while True:
        ''' accept() waits for an incoming connection
        returns connection between client and server --
        connection and client address
        '''
        print('waiting for a connection')
        sock_connection, client_address = sock.accept()

        try:
            print('connection from ', client_address)
            '''reading data from connection with recv()'''
            
            request = sock_connection.recv(1024)
            if request:
	            request = request.decode('utf-8')
	            print('request-header:')
	            print(request)

	            uri = process_http_header(request)
	            #print(uri)
	            if (uri == None):
	                '''send bad request page'''
	                header = 'HTTP/1.1 400 Bad Request \r\n Content-Type: text/html\r\n\r\n'
	                content_bad_req= '<html><head><title>Bad Request</title></head><body>boo! bad request :(</body></html>'

	                sock_connection.send(header.encode('utf-8'))
	                sock_connection.send(content_bad_req.encode('utf-8'))
	              

	            else:
	                curr_working_dir = os.path.dirname(os.path.abspath(__file__))+'/static'
	                print('working dir: ', curr_working_dir)
	                #print('Path: ', curr_working_dir)
	                uri_path = curr_working_dir + '/'+ uri[1:]
	                print('uri_path: ', uri_path)
	                body = b""

	                try:
	                    with open(uri_path, 'rb') as file:
	                        for line in file:
	                            body += line
	                    '''file = open(uri_path, 'rb')
	                    print('file path: ', file)
	                    for line in file:
	                         body += line

	                    file.close()'''
	                    header = 'HTTP/1.1 200 OK \r\n Content-Type: text/html\r\n\r\n'
	                    sock_connection.send(header.encode('utf-8') + body)
	                except IOError:
	                    #print("Cannot open file")
	                    header = 'HTTP/1.1 404 Not Found\r\n Content-Type: text/html\r\n\r\n'
	                    content_not_found = '<html><head><title>Page not found</title></head><body>The page was not found.</body></html>'
	                    sock_connection.send(header.encode('utf-8'))
	                    sock_connection.send(content_not_found.encode('utf-8'))
	                   

		                
	            
        finally:
            '''closing the conection'''
            print('closing connection...')
            sock_connection.close()

