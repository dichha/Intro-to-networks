Q4) Programming question
a) This part of code is in file chat-part-a.py
In console the following command is used to run the file. 
This is for client diane.
	python3 chat-part-a.py diane 127.0.0.1:10000 127.0.0.1:20000
This is for client edward
	python3 chat-part-a.py edward 127.0.0.1:20000 127.0.0.1:10000

b) This part consists complete program. The two files are chat.py and dirservice.py 

	for dirservice ipaddress = 127.0.0.1 and port number = 52000

	dirservice.py is ran using this following command. 
	python3 dirservice.py

	chat.py is ran using the following command.
	
	This is for client diane.
	python3 chat.py diane 127.0.0.10000 127.0.0.1:20000[edward] 127.0.0.1:52000
	
	This is for client edward
	python3 chat.py edward 127.0.0.20000 127.0.0.1:10000[diane] 127.0.0.1:52000
	

Assumption made in this part b is
1) client has to manually reconnect to server if was unsuccessful to retrieve to destination's 
ipaddress. 
2) The lookup is done using username which is a string of letters. 

