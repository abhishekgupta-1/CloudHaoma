import zmq
import sys
import random
import ast
import threading

#python2.7 server.py 1 tcp://127.0.0.1 12345 ["1","2","3"]

class LogEntry(object):
	def __init__(self, clientId, requestId, data, term):
		self._clientId = clientId
		self._requestId = requestId
		self._data = data
		self._term = term

class Log(object):
	def __init__(self, server_id):
		self._firstIndex = 0
		self._length = 1;
		self._entries = [LogEntry(server_id, 0, None, 0), ]

	def push(self, value):
		self._length += 1
		print value, type(value)
		trans = LogEntry(value['_clientId'], value['_requestId'], value['_data'], value['_term'])
		self._entries.append(trans)

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
port_no2 = '5000'
clusterMembers = ast.literal_eval(sys.argv[4])
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
lastApplied = 0
nextIndex = {}
matchIndex = {}
recoveryMode = False
recoveryPrevLogIndex = 0
grantedVotes = 0
election = random.randint(150, 300)
heartbeatTime = 25
commitTime = 50
log = Log(server_id)
shift = False
shiftHeart = False
electionTimeCall = False
heartbeatTimeCall = False
#This function will called every electionTime


for member in clusterMembers:
	matchIndex[member] = 0
	nextIndex[member] = 1

def sendMessage(destid, msg):
	msg['dest'] = destid
	sender_socket.send_json(msg)


def electionTimeout():
	global currentTerm, electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
	global server_id, shift
	if electionTimeCall == True:
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
	if shift:
		electionTimeCall = True
		shift = False
	threading.Timer(.5, electionTimeout).start()


def heartbeatTimeout():
	global heartbeatTimeCall, shift, currentTerm, server_id, shiftHeart
	global electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
	if heartbeatTimeCall == True:
		msg = {'rpc':'appendEntries'
		, 'term':currentTerm
		, 'leaderId': server_id
		, 'prevLogIndex':log._length-1
		, 'prevLogTerm':log._entries[-1]._term
		, 'entries' : []
		, 'leaderCommit':commitIndex};
		for destid in clusterMembers:
			if destid != server_id:
				sendMessage(destid, msg)
		electionTimeCall = False
		shift = False
	if shiftHeart == True:
		heartbeatTimeCall = True
		shiftHeart = False
	threading.Timer(.025, heartbeatTimeout).start()

electionTimeout()
electionTimeCall = True
heartbeatTimeout()

#Bad!! TODO: make this async IO
def processEntries(upTo):
	global server_id, state,lastApplied, log
	for entryIndex in range(lastApplied, upTo):
		entry = log._entries[entryIndex]
		if state == 'l':
			clientId = entry._clientId
			requestId = entry._requestId
			msg = {'dest':clientId
			, 'requestId':'requestId'
			, 'status' : 'Success'};
			sendMessage(clientId, msg);
		write_to_file(json_loads(entry._data))
	lastApplied = upTo



def requestVote(term, candidateId, lastLogIndex, lastLogTerm):
	global heartbeatTimeCall, shift, currentTerm, electionTimeCall, state, votedFor, grantedVotes, clusterMember, lastKnownLeaderID, log
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
	global heartbeatTimeCall, currentTerm, electionTimeCall, state, votedFor
	global server_id, grantedVotes, clusterMember, lastKnownLeaderID, log
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


def appendEntries(term, leaderId, prevLogIndex, prevLogTerm, entries, leaderCommit):
	global currentTerm, electionTimeCall, lastKnownLeaderID, currentTerm, log, shift
	global recoveryMode, commitIndex, server_id
	processEn= False
	msg = {}
	if term>=currentTerm:
		electionTimeCall = False
		shift = False
		if (lastKnownLeaderID != leaderId):
			print("Election result %d is the new leader"%(leaderId))
		lastKnownLeaderID = leaderId
		if term > currentTerm :
			currentTerm = term
		log_length = log._length
		log_firstIndex = log._firstIndex
		log_prevTerm = 10000000 #Possibly faulty!
		if prevLogIndex < log_length:
			log_prevTerm = log._entries[prevLogIndex]._term

		if (prevLogIndex < log_length and (log_length==log_firstIndex or log_prevTerm==prevLogTerm)):
			if recoveryMode:
				print("Last matching entry found. Exiting recovery mode.!")
			recoveryMode = False
			for entry in entries:
				log.push(entry)
			msg = {'rpc':'replyAppendEntries'
			, 'term':currentTerm
			, 'followerId':server_id
			, 'entriesToAppend': len(entries)
			, 'success':True};
			if leaderCommit > commitIndex:
				commitIndex = min(leaderCommit, log._length)
				processEn = True
				#TODO processEntries
			electionTimeCall = False #check this statement if bug occurs
			shift = True
		elif (recoveryMode==False or (recoveryMode and prevLogIndex < recoveryPrevLogIndex)):
			while prevLogIndex < log._length:
				log.pop()
			if recoveryMode == False:
				print("Log is outdated. Entering recovering mode.")
			recoveryPrevLogIndex = prevLogIndex
			msg = {'rpc':'replyAppendEntries'
			, 'term':currentTerm
			, 'followerId':server_id
			, 'entriesToAppend': prevLogIndex
			, 'success':False};
	else:
		msg = {'rpc':'replyAppendEntries'
		, 'term':currentTerm
		, 'followerId':server_id
		, 'entriesToAppend': prevLogIndex
		, 'success':False};
	if msg != {}:
		# print ("leaderid = %s"%(leaderId))
		sendMessage(leaderId, msg)
	if processEn:
		processEntries(commitIndex)


def replyAppendEntries(term, followerId, entriesToAppend, success):
	global currentTerm, heartbeatTimeCall, grantedVotes, votedFor, state
	global maybeNeedToCommit, matchIndex, nextIndex, log, recoveryMode, server_id
	if (state == 'l' and term >= currentTerm):
		if term > currentTerm:
			currentTerm = term
			state = 'f'
			grantedVotes = 0
			votedFor= None
			heartbeatTimeCall = False
		elif success:
			matchIndex[followerId] += entriesToAppend
			maybeNeedToCommit = True
			if (nextIndex[followerId]<log._length):
				msg = {'rpc':'appendEntries'
				, 'term':currentTerm
				, 'leaderId':server_id
				, 'prevLogIndex':nextIndex[followerId]-1
				, 'prevLogTerm':log._entries[nextIndex[followerId]-1]._term
				, 'entries': log.slice(nextIndex[followerId], min(log._length, nextIndex[followerId]+100))
				, 'leaderCommit':commitIndex}
				nextIndex[followerId]+=min(log._length,nextIndex[followerId]+100)-nextIndex[followerId]
				if nextIndex[followerId] == log._length:
					if recoveryMode:
						print("Follower %d log should be now in sync. Exiting recovery mode."%(followerId))
						recoveryMode = False
				sendMessage(followerId, msg)
				commitEntries()
		else:
			if recoveryMode == False: print("Follower %d log is outdated. Entering recovery mode."%(followerId))
			recoveryMode = True
			nextIndex[followerId] = entriesToAppend
			matchIndex[followerId] = nextIndex[followerId]-1
			if log._entries[nextIndex[followerId]-1] != None:
				msg = {'rpc':'appendEntries'
				, 'term':currentTerm
				, 'leaderId':server_id
				, 'prevLogIndex':nextIndex[followerId]-1
				, 'prevLogTerm':log._entries[nextIndex[followerId]-1]._term
				, 'entries': [log._entries[nextIndex[followerId]].__dict__]
				, 'leaderCommit':commitIndex}
				nextIndex[followerId] += 1
				sendMessage(followerId, msg)
			else: #Last log is behind oldest entry still in the log
				pass


def newNullEntry():
	global server_id, currentTerm
	dummy = LogEntry(server_id, 0, {type:'NUL'}, currentTerm)
	msg = {'rpc':'appendEntries'
		, 'term':currentTerm
		, 'leaderId':server_id
		, 'prevLogIndex':log._length-1
		, 'prevLogTerm':log._entries[log._length-1]._term
		, 'entries': [dummy.__dict__]
		, 'leaderCommit':commitIndex}	


def write_to_file(msg):
	with open(msg['fileName'], "a") as myfile:
	    myfile.write("%s"%(msg['data']))




#commitIndex - Start commit from this index
def commitEntries():
	global maybeNeedToCommit, commitIndex, clusterMembers, server_id
	global newCommitIndex, currentTerm, log
	processEn = False
	if maybeNeedToCommit:
		newCommitIndex = commitIndex-1
	while True:
		newCommitIndex += 1
		numReplicas = 1
		for node in clusterMembers:
			if node != server_id:
				if matchIndex[node] >= newCommitIndex: numReplicas+=1
		if numReplicas <= len(clusterMembers)/2:
			break
	if log._entries[newCommitIndex]._term == currentTerm:
		commitIndex = newCommitIndex
		processEn = True
	maybeNeedToCommit = False
	if processEn:
		processEntries(commitIndex+1) #Why commitIndex + 1??


def addEntry(requestId, request_data, clientId):
	global currentTerm, state, server_id, log, heartbeatTimeCall, lastKnownLeaderID
	global heartbeatTimeCall, shiftHeart, shift, electionTimeCall
	if state == 'l':
		entry = LogEntry(clientId, requestId, request_data, currentTerm)
		msg = {'rpc':'appendEntries'
		, 'term':currentTerm
		, 'leaderId':server_id
		, 'prevLogIndex': (log._length)
		, 'prevLogTerm' : log._entries[-1]._term
		, 'entries': [entry.__dict__]
		, 'leaderCommit':commitIndex};
		for node in clusterMembers:
			if node != server_id:
				if nextIndex[node] == log._length:
					nextIndex[node] += 1
					sendMessage(node, msg)
		log.push(entry.__dict__)
		heartbeatTimeCall = False
		shiftHeart = True
		electionTimeCall = False
		shift = True
	elif lastKnownLeaderID != None: #forward to leader
		msg = {'clientId':clientId
		, 'requestId' : requestId
		, 'request_data' : request_data
		, 'rpc':'addEntry'};
		sendMessage(lastKnownLeaderID, msg);



#Life
while True:
	message = receiver_socket.recv()
	sender_id, message = message.split(" ", 1)
	message = ast.literal_eval(message)
	print sender_id, message, type(message)
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
	elif rpc == 'replyAppendEntries':
		replyAppendEntries(message['term']
			, message['followerId']
			, message['entriesToAppend']
			, message['success'])
	elif rpc == 'addEntry':
		addEntry(message['requestId']
			, message['request_data']
			, message['clientId'])



		

  # msg = {'clientId':serverID
  # , 'dest': ''
  # , 'requestId' : request_id
  # , 'request_data' : '123'
  # , 'rpc':'addEntry'
  # , 'fileInfo' : 'bee.txt'};