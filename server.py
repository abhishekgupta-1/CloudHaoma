import zmq
import sys

class LogEntry(Object):
	def __init__(self, clientId, clientSeqNum, data, term):
		self._clientId = clientId
		self._clientSeqNum = clientSeqNum
		self._data = data
		self._term = term

class Log(Object):
	def __init__(self, server_id):
		self._firstIndex = 0
		self._length = 1;
		self._entries = []
		self._serverid = server_id
		pass
	def push(self, value):
		self._length += 1
		self._entries.append(LogEntry(self._server_id, 0, None, 0))

	def pop(self):
		self._length -= 1
		self._entries.pop()

	def shift(self):
		pass

	def slice(self, from1, to):
		return self._entries[from1:to]





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


currentTerm = 0
state = 'f'
votedFor = None
lastKnownLeaderID = None
commitIndex = 0


i = 0
while True:
	sender_socket.send_json({"dest":server_id, "i" : i})
	print "here"
	data = receiver_socket.recv()
	print data
	i+=1


