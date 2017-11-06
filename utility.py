
def writeToPersistentStore():
	global currentTerm, votedFor, log
	dic = {"currentTerm": currentTerm, "votedFor": votedFor, "log": log }
	with open("checkpoint.pkl", "wb") as outFile:
		pickle.dump(dic, outFile, pickle.HIGHEST_PROTOCOL)
		# pickle.dump(log, outFile, pickle.HIGHEST_PROTOCOL)

def readFromPersistentStore():
	global currentTerm, votedFor, log
	with open("checkpoint.pkl", "rb") as inFile:
		newDic = pickle.load(inFile)
		currentTerm = newDic['currentTerm']
		votedFor = newDic['votedFor']
		log = newDic['log']


def write_to_file(msg):
	if msg is not None:
		with open(msg['fileName'], "a") as myfile:
		    myfile.write("%s"%(msg['fileData']))
