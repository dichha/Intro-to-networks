import socket
import struct
import select
import sys

'''
struct module performs conversion between Python values and C structs represented as Python 
strings. This can be used in handling binary data stored in files or from netwoek connections, 
among other sources

select module provides access to the select(). select.select() is a straightforward interface to the Unix
select system call. 
'''


def parse_ip_port(ip_port):
    ip_port_list = ip_port.split(':')
    ip = ip_port_list[0]
    port = ip_port_list[1]
    return (ip, int(port))

def encode_chat_msg(seqnum, UID, DID, msg, version=150,):
	header_buf = bytearray(36)
	UID = UID + ' '*(16 - len(UID))
	DID = DID + ' '*(16 - len(DID))

	header_buf = struct.pack('!HH16s16s', version, seqnum, UID.encode('utf-8'), DID.encode('utf-8'))

	''' max size of text msg = 1024 characters. msg size not known in advance'''
	header_buf = header_buf + msg.encode('UTF-8')

	return header_buf

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

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    arg_list = sys.argv
    print(arg_list)
    UID = arg_list[1]
    uip_port = arg_list[2]
    uip_port = parse_ip_port(uip_port)
    DID = arg_list[3]
    dip_port = parse_ip_port(DID)
    sock.bind(uip_port)
 
    seqnum = 0

    try: 
    	while True:
            user_input = None 
            print(UID, '>> ', end='', flush=True)
           
            rlist, wlist, elist = select.select([sock, sys.stdin], [], [])
            #print('Select completed', rlist, wlist, elist)

            if sys.stdin in rlist:
            	#if you do input from when the sys.stdin has data available to read from,
            	# it will NOT BLOCK

            	user_input = input()
            	#print('sending "%s"' % message)
            	print('sending "%s"' % user_input)
            	seqnum += 1
            	pkts = encode_chat_msg(seqnum, UID, DID, user_input)
            	#print('encoded msg "%s"' % pkts)


            	#user_input_bytes = user_input.encode('UTF-8')
            	#sent = sock.sendto(user_input_bytes, server_address)
            	sent = sock.sendto(pkts, dip_port)

            if sock in rlist:
            	#data is pending on the socket
            	#reading from the socket will NOT block
                data, address = sock.recvfrom(4096)
                decoded_msg = decode_chat_msg(data)
                print('Message: %s'%decoded_msg[3])
                #print('received "%s" from ipaddress "%s" and port number "%s"'%(decoded_msg[3], address[0], address[1]))  
                print('sent by %s from ipaddress %s port number %s'%((decoded_msg[1]).strip(), address[0], address[1]))

    finally:
    	print('closing socket...')
    	sock.close()