import socket 
import sys
import struct

''' removes spaces that was inserted while encoding'''
def strip_space(data):
	return data.strip()


''' inserts user_id and their ip address and port number in a global dictionary'''
def register(dir_dict, UID, uip_port):
	UID = strip_space(UID)
	uip_port = strip_space(uip_port)
	dir_dict[UID] = uid_port
	return dir_dict

''' unpacks packets that was sent by clients for registration '''
def decode_registration(regis_buf):
	#print(len(regis_buf))
	#print(struct.calcsize(regis_buf))
	pkt_format = '!16s16s16s'
	pkt_size = struct.calcsize(pkt_format)
	tup_val = struct.unpack(pkt_format, regis_buf[:pkt_size])
	#print(tup_val)
	(UID, uip_port, DID) = tup_val
	UID = UID.decode('utf-8')
	DID = DID.decode('utf-8')
	uip_port = uip_port.decode('utf-8')
	return(UID, uip_port, DID)

''' looks up ipaddress of destination and returns appropriate response'''
def lookup_dest_ipaddr(dir_dict, query):
	query = strip_space(query)
	#print('query:  %s'%query)
	if query in dir_dict.keys():
		error_code = 400
		dest_ipaddr = dir_dict[query]	
	else:
		error_code = 600
		dest_ipaddr = None
	return (error_code, dest_ipaddr)

''' encodes error response to packets that will get sent to a client'''
def encode_error_response(error_code):
	header_buf = bytearray(18)
	ipaddress = '0'*16
	header_buf = struct.pack('!H16s', error_code, ipaddress.encode('utf-8'))
	error_response  = "Unfortunately your destination's ipaddress is not found. Please try after 5 seconds."

	header_buf = header_buf + error_response.encode('utf-8')
	return header_buf

'''encodes success response to packets that will get sent to a client'''
def encode_success_response(error_code, dest_ipaddr):
	header_buf = bytearray(18)
	dest_ipaddr = dest_ipaddr + ' '*(16-len(dest_ipaddr))
	header_buf = struct.pack('!H16s', error_code, dest_ipaddr.encode('utf-8'))
	return header_buf

if __name__ == '__main__':

	#a global dictionary
	dir_dict = dict() 

	#create a TCP/IP socket
	print('creating a TCP socket')
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_address = ('localhost', 52000)
	#bind the socket to the port
	print('starting up on %s port %s' % server_address)
	#bind() is used to associalte the socket with the server address
	sock.bind(server_address)

	'''calling listen() puts the socket into a server mode, and accept() 
	waits for an incoming connection'''

	#listen for incoming connection

	sock.listen(1)

	while True:
		# accept() waits for an incoming connection
		# returns connection between client and server -- connection and the address of the client

		print('waiting for a connection')

		connection, client_address = sock.accept()
		try:
			print('connection from', client_address)
			while True:
				#reading data from the connection with recv()
				data= connection.recv(4096)
				#print(type(data.decode('utf-8')))
				#print(len(data))
				#print('received "%s"'%data)

				
				if data:
					#decoding received registration packets	
					UID, uid_port, DID = decode_registration(data)
					print('UID: %s uid_port: %s DID: %s'%(UID, uid_port, DID))
					#registering user and their ipaddress
					dir_dict = register(dir_dict, UID, uid_port)
					#print(dir_dict)
					
					#printing out registered user and their ipaddress
					for key, value in dir_dict.items():
						print('%s: %s'%(key, value))

					#lookup for destination's ipaddress
					error_code, dest_ipaddr = lookup_dest_ipaddr(dir_dict, DID)

					print('error code: %s' %error_code)

					#checking error_code 
					if(error_code == 600):
						error_msg_pkt = encode_error_response(error_code)
						connection.sendall(error_msg_pkt)
						
					else:
						success_msg_pkt = encode_success_response(error_code, dest_ipaddr)
						connection.sendall(success_msg_pkt)
						break #break for getting out of loop and listen for new incoming connection

					

					#print('sending data back to the client')
					#connection.sendall(data)
				else:
					print('no more data from', client_address)
					break
		finally:
			#clean up the connection
			connection.close()