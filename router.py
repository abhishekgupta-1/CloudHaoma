import sys
import zmq
import json
import ast

#python2.7 router.py 12345 ["5"] false

debug = (sys.argv[3] == "true")
context = zmq.Context()
receiver_socket = context.socket(zmq.PULL)
receiver_socket.bind("tcp://*:"+str(sys.argv[1]))
sender_socket = context.socket(zmq.PUB)
sender_socket.bind("tcp://*:5000");

client_socket = context.socket(zmq.PUSH)
client_socket.bind("tcp://*:5002")

Servers = ast.literal_eval(sys.argv[2])
Servers = [int(x) for x in Servers]

while True:
	data = receiver_socket.recv_json()
	dest_id = str(data['dest'])
	print data
	if dest_id not in Servers:
		sender_socket.send("%s %s"%((dest_id), data))
	else:
		client_socket.send("%s"%(json.dumps(data)))