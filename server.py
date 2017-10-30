import zmq
import sys


context = zmq.Context()


server_id = int(sys.argv[1])
router_address = sys.argv[2]
port_no = sys.argv[3]
port_no2 = sys.argv[4]
sender_socket = context.socket(zmq.PUSH)

sender_socket.connect(router_address +":"+ port_no)

receiver_socket = context.socket(zmq.SUB)
receiver_socket.setsockopt(zmq.SUBSCRIBE, str(server_id))
receiver_socket.connect(router_address + ":" +port_no2)

i = 0
while True:
	sender_socket.send_json({"dest":server_id, "i" : i})
	print "here"
	data = receiver_socket.recv()
	print data
	i+=1
