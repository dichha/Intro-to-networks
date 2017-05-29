import select
import socket
import sys
import queue
import os
import re


def process_data(data):
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

    data_list = data.splitlines()
    data_list = data_list[:-1]  # -1 for taking last empty item
    if (len(data_list) == 0):
        print('Empty data')
        return (None, None)

    verb_line = data_list.pop(0)
    print("request header: ", verb_line)
    regex_header_verb = re.compile(r'(GET\s{1}|POST\s{1})[A-Za-z0-9\.\/]*\s{1}HTTP\/1\.1')
    verb_uri_match = bool(regex_header_verb.match(verb_line))

    if verb_uri_match == False:
        print('Wrong request URI')
        return None, None
    (verb, uri, version) = verb_line.split()
    if verb == 'GET':
        print("Request data: ", data_list)
        regex_header_key_val = re.compile(r'\s*(?P<key>.+\S)\s*:\s+(?P<value>.*\S)\s*')
        for header in data_list:
            # print(header)
            match = bool(regex_header_key_val.match(header))
            if match == False:
                '''write code for bad format and send HTTP Bad Request response'''
                print("bad format")
                return None, None
        return verb, uri
    if verb == 'POST':
        print("In POST block")
        print('Request data: ', data_list)
        key_val_dict = {}
        content_list = data.split('\r\n\r\n')
        header_info = content_list[0].splitlines()[1:]#file path and verb already extracted
        key_val = content_list[1]
        if(len(key_val) == 0):
            print("Not a complete form")
            return None, None
        print("key-val", key_val)
        '''fname=diane&lname=rai&gender=female'''
        key_val_list = key_val.split('&')
        for kv in key_val_list:
            kv = kv.split('=')
            key_val_dict[kv[0]] = kv[1]
        print('Iterating over key_val_dict')
        for key, val in key_val_dict.items():
            print('%s:%s'%(key,val))

        response_page = uri[1:]
        key_val_dict['response_page'] = response_page
        return verb, key_val_dict


def file_path(context):
    curr_working_dir = os.path.dirname(os.path.abspath(__file__)) + '\static'
    print('working dir: ', curr_working_dir)
    # print('Path: ', curr_working_dir)
    uri_path = curr_working_dir + '\\' + context
    print('uri_path: ', uri_path)
    return uri_path


def get_bad_request_header():
    bad_request_header = 'HTTP/1.1 400 Bad Request \r\n Content-Type: text/html\r\n\r\n'
    return bad_request_header


def get_success_response_header():
    success_response_header = 'HTTP/1.1 200 OK \r\n Content-Type: text/html \r\n\r\n'
    return success_response_header


def get_page_not_found_response_header():
    page_not_found_response_header = 'HTTP/1.1 404 Not Found \r\n Content-Type: text/html \r\n\r\n'
    return page_not_found_response_header


def get_page_not_found_body():
    page_not_found_body = '<html><head><title>Page not found</title></head><body>The page was not found.</body></html>'
    return page_not_found_body


def get_cur_working_dir():
    curr_working_dir = os.path.dirname(os.path.abspath(__file__)) + '/static'
    return curr_working_dir




if __name__ == '__main__':
    '''arguments for server hostname and port'''
    arg_list = sys.argv
    hostname = arg_list[1]
    port = int(arg_list[2])
    server_address = (hostname, port)
    # print(server_address)


    # Create a TCP/IP socket
    print('creating a TCP socket')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server.setblocking(0)  # blocking is False ==> non-blocking socket

    # Bind the socket to the port
    print('starting up on %s port %s' % server_address)
    server.bind(server_address)

    # Listen to incoming connections
    server.listen(5)  # listening for upto 5 connections

    # Sockets from which we expect to read  == producer
    inputs = [server]

    # Sockets to which we expect to write == consumer
    outputs = []

    # Outgoing message queues (socket: Queue)
    client_queues = {}

    while True:
        # Wait for at least one of the sockets to be ready for processing
        print('\n waiting for the next event')
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)

        # handle inputs
        for s in readable:
            if s is server:
                # A "readable" server is ready to accept a client_socket connection

                client_socket, client_address = s.accept()
                print('new client_socket from ', client_address)
                client_socket.setblocking(0)  # non-blocking client_socket
                inputs.append(client_socket)

                # Give the client_socket a queue for data we want to send
                client_queues[client_socket] = queue.Queue()
            else:

                data = s.recv(1024)

                if data:
                    # A readable client socket has data
                    print('received %s from %s' % (data, s.getpeername()))
                    data = data.decode('utf-8')
                    verb, context = process_data(data)
                    print("context: ", context)
                    if context == None:
                        '''send bad request page'''
                        header = 'HTTP/1.1 400 Bad Request \r\n Content-Type: text/html\r\n\r\n'
                        content_bad_req = '<html><head><title>Bad Request</title></head><body>boo! bad request :(</body></html>'
                        content = header.encode('utf-8') + content_bad_req.encode('utf-8')
                        client_queues[s].put(content)
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                    elif isinstance(context,dict) and verb == 'POST':
                        print("In post redirect")
                        curr_working_dir = get_cur_working_dir()
                        uri_path = curr_working_dir + '/' + context['response_page']
                        print('URI: ', uri_path)
                        text = ' '
                        with open(uri_path, 'r') as infile:
                            text = infile.read()
                            for key in context:
                                text = text.replace('{{' + key + '}}', context[key])
                            print(text)
                        with open(uri_path, 'w') as infile:
                            infile.write(text)

                        success_response_header = get_success_response_header()
                        body = b""

                        try:
                            with open(uri_path, 'rb') as file:
                                for line in file:
                                    body += line

                            content = success_response_header.encode('utf-8') + body
                            client_queues[s].put(content)

                            # Add output channel for response
                            if s not in outputs:
                                outputs.append(s)
                        except IOError:
                            print("Cannot open file")
                            page_not_found_response_header = get_page_not_found_response_header()
                            content_not_found = get_page_not_found_body()

                            content = page_not_found_response_header.encode('utf-8') + content_not_found.encode('utf-8')
                            client_queues[s].put(content)

                            # Add output channel for response
                            if s not in outputs:
                                outputs.append(s)


                    else:
                        curr_working_dir = get_cur_working_dir()
                        print('working dir: ', curr_working_dir)
                        uri_path = curr_working_dir + '/' + context[1:]#context here is a uri filename
                        print('URI: ', uri_path)
                        success_response_header = get_success_response_header()
                        body = b""

                        try:
                            with open(uri_path, 'rb') as file:
                                for line in file:
                                    body += line

                            content = success_response_header.encode('utf-8') + body
                            client_queues[s].put(content)

                            # Add output channel for response
                            if s not in outputs:
                                outputs.append(s)
                        except IOError:
                            print("Cannot open file")
                            page_not_found_response_header = get_page_not_found_response_header()
                            content_not_found = get_page_not_found_body()

                            content = page_not_found_response_header.encode('utf-8') + content_not_found.encode('utf-8')
                            client_queues[s].put(content)

                            # Add output channel for response
                            if s not in outputs:
                                outputs.append(s)
                else:
                    # interpret empty results as closed client_socket
                    print('closing ', client_address, 'after reading no data')
                    # Stop listening for input on the client_socket
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del client_queues[s]

        # handle outputs
        for s in writeable:
            try:
                next_content = client_queues[s].get_nowait()  # equivalent to get(False)
            except queue.Empty:
                # No contents waiting so stop checking for writability
                print('output queue for ', s.getpeername(), ' is empty.')
                outputs.remove(s)
            else:
                print('sending "%s" to %s' % (next_content, s.getpeername()))
                s.send(next_content)

        # Handle "exceptional conditions"
        for s in exceptional:
            print('handling exceptional condition for ', s.getpeername())
            # stop listening for inut on the client_socket
            inputs.remove(s)

            if s in outputs:
                outputs.remove(s)
            s.close()

            # remove message queue
            del client_queues[s]




