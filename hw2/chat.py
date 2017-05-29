import socket
import sys
import struct
import select
import time

'''convert ip and port number to a tuple'''
def parse_ip_port(ip_port):
    ip_port_list = ip_port.split(':')
    ip = ip_port_list[0]
    port = ip_port_list[1]
    return (ip, int(port))

'''convert ip and port number and DID to a tuple'''
def parse_ip_port_did(ip_port_did):
    ip_port_did_list = ip_port_did.split(':')
    ip = ip_port_did_list[0]
    port_did_list = ip_port_did_list[1].split('[')
    port = port_did_list[0]
    did = port_did_list[1]
    did = did[:-1]
    return (ip, int(port), did)

'''make packets for sending registration'''
def encode_registration(UID, user_addr, DID):
    header_buf = bytearray(48)
    UID = UID + ' '*(16-len(UID))
    DID = DID + ' '*(16-len(DID))
    user_addr = user_addr + ' '*(16-len(user_addr))

    header_buf = struct.pack('!16s16s16s', UID.encode('utf-8'), user_addr.encode('utf-8'), DID.encode('utf-8'))

    return header_buf

''' decoding response got from dirservice.py'''
def decode_dir_response(dir_buff):
	tup_val = struct.unpack('!H16s', dir_buff[:18])
	(error_code, dest_ipaddr) = tup_val
	dest_ipaddr = dest_ipaddr.decode('utf-8')
	msg = dir_buff[18:].decode('utf-8')

	return (error_code, dest_ipaddr, msg)

''' converting chat msg to packets to be sent to its destination'''
def encode_chat_msg(seqnum, UID, DID, msg, version=150,):
	header_buf = bytearray(36)
	UID = UID + ' '*(16 - len(UID))
	DID = DID + ' '*(16 - len(DID))

	header_buf = struct.pack('!HH16s16s', version, seqnum, UID.encode('utf-8'), DID.encode('utf-8'))

	''' max size of text msg = 1024 characters. msg size not known in advance'''
	header_buf = header_buf + msg.encode('UTF-8')
	return header_buf

'''decoding chat message reveived'''	
def decode_chat_msg(msg_buf):
    #print(struct.calcsize(msg_buf))
    tup_val = struct.unpack('!HH16s16s', msg_buf[:36])
    print(tup_val)
    (version, seqnum, UID, DID) = tup_val
    UID = UID.decode('utf-8')
    DID = DID.decode('utf-8')
    msg = msg_buf[36:].decode('utf-8')
    return(seqnum, UID, DID, msg)


if __name__ == '__main__':

	''' gathering arguments '''
	arg_list = sys.argv
	UID = arg_list[1] 


	uip_port = arg_list[2]
	#print(uip_port)
	uip_port_reg = uip_port
	uip_port = parse_ip_port(uip_port)
	
	dip_port_did = arg_list[3]
	
	dip_port_did = parse_ip_port_did(dip_port_did)
	dip_port = ((dip_port_did[0], int(dip_port_did[1])))
	#print(dip_port)
	#DID_pkts = str(dip_port_did[0])+':'+str(dip_port_did[1])
	#print(DID_pkts)

	DID = dip_port_did[2]#username

	dir_ip_port = arg_list[4]
	dir_ip_port = parse_ip_port(dir_ip_port)


	#create a TCP/IP socket
	print('creating a TCP/IP socket')
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#connect the socket to the port where the server is listening
	#server_address = ('localhost', 51000)
	server_address = dir_ip_port

	print('connecting to %s port %s' % server_address)
	sock.connect(server_address)


	try :
		#send data
		#message = 'This is the message. It will be repeated.'
		#print('sending "%s"' % message)
		#sock.sendall(message.encode('UTF-8'))
		regis_pkts = encode_registration(UID, uip_port_reg, DID)
		print('sending query for %s'%regis_pkts)
		sock.sendall(regis_pkts)

		#look for the response

		print('receiving from dirservice')
		data = sock.recv(4096)
		if data:
			error_code, dest_ipaddr, msg  = decode_dir_response(data)
			if(error_code == 600):
				print(msg)

			else:
				print('dest_ipaddr %s' % dest_ipaddr)
				''' This is where UDP protocol is used to chat between clients once a connection is established'''
				udp_sock_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				udp_sock_listener.bind(uip_port)
				seqnum = 0
				dest_ipaddr_pkts = dest_ipaddr
				dest_ipaddr = parse_ip_port(dest_ipaddr)
		
				try: 
					while True:
						user_input = None
						print(UID, '>> ', end='', flush=True)

						rlist, wlist, elist = select.select([udp_sock_listener, sys.stdin], [], [])
						#print('Select completed', rlist, wlist, elist)

						if sys.stdin in rlist:
							#if you do input when the sys.stdin has data available to read 
							# it will not block

							user_input = input()
							print('sending "%s"' % user_input)
							seqnum += 1
							pkts = encode_chat_msg(seqnum, UID, dest_ipaddr_pkts, user_input)
							sent = udp_sock_listener.sendto(pkts, dest_ipaddr)


						if udp_sock_listener in rlist:
							data, address = udp_sock_listener.recvfrom(4096)
							decoded_msg = decode_chat_msg(data)
							#print('received "%s" from ipaddress "%s" and port number "%s"'%(decoded_msg[3], address[0], address[1]))
							print('Message: %s'%decoded_msg[3])
							print('sent by %s from ipaddress %s port number %s'%((decoded_msg[1]).strip(),address[0], address[1]))


				finally: 
					print('closing UDP socket')
					udp_sock_listener.close()







			#amount_received += len(data)

		
		#print('received "%s"' % data)


	finally:
		print('closing socket')
		sock.close()