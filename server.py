import zmq
import sys
import random
import ast
import threading

class LogEntry(object):
	def __init__(self, clientId, clientSeqNum, data, term):
		self._clientId = clientId
		self._clientSeqNum = clientSeqNum
		self._data = data
		self._term = term

class Log(object):
	def __init__(self, server_id):
		self._firstIndex = 0
		self._length = 1;
		self._entries = [LogEntry(server_id, 0, None, 0)]

	def push(self, value):
		self._length += 1
		self._entries.append(value)

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
clusterMembers = ast.literal_eval(sys.argv[5])
clusterMembers = [int(x) for x in clusterMembers]
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
maybeNeedToCommit = False
lastApplied = False
maxAppliedEntriesInLog = 10000
hardLogSizeLimit = 100000
nextIndex = {}
matchIndex = {}
recoveryMode = False
recoveryPrevLogIndex = 0
grantedVotes = 0
election = random.randint(150, 300)
heartbeatTime = 25
commitTime = 50
log = Log(server_id)

electionTimeCall = False
heartbeatTimeCall = False
#This function will called every electionTime

def sendMessage(destid, msg):
	msg['dest'] = destid
	sender_socket.send_json(msg)


def electionTimeout():
	global currentTerm, electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
	if electionTimeCall == True:
		print("here")
		if lastKnownLeaderID == None:
			print("No known leader for me, starting election!")
		else:
			print("No heartbeat received from leader starting election!")
		currentTerm += 1
		state = 'c'
		votedFor = server_id
		grantedVotes = 1
		msg = {'rpc':'requestVote'
		, 'term':currentTerm
		, 'candidateId':server_id
		, 'lastLogIndex':log._length-1
		, 'lastLogTerm':log._entries[-1]._term};
		for destid in clusterMembers:
			if destid != server_id:
				sendMessage(destid, msg)
	electionTimeCall = True
	threading.Timer(.5, electionTimeout).start()

def heartbeatTimeout():
	global heartbeatTimeCall, currentTerm, electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
	if heartbeatTimeCall == True:
		msg = {'rpc':'appendEntries'
		, 'term':currentTerm
		, 'leaderId': server_id
		, 'prevLogIndex':log._length-1
		, 'prevLogTerm':log._entries[-1]._term
		, 'entries' : []
		, 'leaderCommit':commitIndex};
		for destid in clusterMembers:
			sendMessage(destid, msg)
		electionTimeCall = False
	threading.Timer(.025, heartbeatTimeout).start()

electionTimeout()
heartbeatTimeout()




def appendEntries(term, leaderId, prevLogIndex, prevLogterm, entries, leaderCommit):
	pass


def requestVote(term, candidateId, lastLogIndex, lastLogTerm):
	global heartbeatTimeCall, currentTerm, electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
	msg = []
	if term >= currentTerm:
		if term > currentTerm : #I am in the past
			print("Election in progress!")
			currentTerm = term
			if (state == 'l'): 
				print("Demoting to follower state.")
			state = 'f'
			votedFor = None
			recoveryMode = None
			heartbeatTimeCall = False
		if (votedFor == None or votedFor==candidateId) \
		and (log._length==log._firstIndex or lastLogTerm >  log._entries[-1]._term or (lastLogTerm == log._entries[-1]._term and lastLogIndex>=log._length-1)):
			votedFor = candidateId
			print("Vote given to candidate %s"%(candidateId))
			msg = {'rpc':'replyVote', 'term':currentTerm, 'voteGranted':True};
		else:
			msg = {'rpc':'replyVote', 'term':currentTerm, 'voteGranted':False};
	else:  #Sender is In the Past
		msg = {'rpc':'replyVote', 'term':currentTerm, 'voteGranted':False}; 
	sendMessage(candidateId, msg)


def replyVote(term, voteGranted):
	global heartbeatTimeCall, currentTerm, electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
	if term > currentTerm:
		currentTerm = term
		state = 'f'
		grantedVotes = 0
		votedFor = None
	elif voteGranted==True and term==currentTerm and state=='c':
		grantedVotes += 1
		print("Received vote")
		if grantedVotes > len(clusterMembers)/2:
			print("Election win. Say Hi to new leader.")
			state = 'l'
			lastKnownLeaderID = server_id
			grantedVotes = 0
			for destid in clusterMembers:
				if destid != server_id:
					nextIndex[destid] = log._length
					matchIndex[destid] = log._length-1
			newNullEntry()
			heartbeatTimeCall = True


def newNullEntry():
	pass



#Life
while True:
	message = receiver_socket.recv()
	_, message = message.split(" ", 1)
	message = ast.literal_eval(message)
	print message, type(message)
	rpc = message['rpc']
	if rpc == 'appendEntries':
		appendEntries(message['term'],
			message['leaderId'],
			message['prevLogIndex'],
			message['prevLogTerm'],
			message['entries'],
			message['leaderCommit'])
	elif rpc == 'requestVote':
		requestVote(message['term']
			, message['candidateId']
			, message['lastLogIndex']
			, message['lastLogTerm'])
	elif rpc == 'replyVote':
		replyVote(message['term'], message['voteGranted'])
	