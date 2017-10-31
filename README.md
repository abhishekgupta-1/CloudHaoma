Run the following commands on all the nodes of the cluster

Python version 2.7

1. sudo apt-get install nodejs nodejs-legacy npm libzmq-dev git
2. pip install pyzmq-static
2. Open Terminal in the base directory of the project
3. npm install
4. pip install zmq


Network topology is star.

Run the following on the designated router.
1.) python2.7 router.py 12345 ["6"] false


Run the following on the cluster nodes (you may include router also (Let IPADDRESS of router node for this be 127.0.0.1):-
1.) python2.7 server.py 1 tcp://127.0.0.1 12345 ["1","2","3","4","5"] on node1
2.) python2.7 server.py 2 tcp://127.0.0.1 12345 ["1","2","3","4","5"] on node2
3.) python2.7 server.py 3 tcp://127.0.0.1 12345 ["1","2","3","4","5"] on node3
Similary on the rest of the two nodes


Run the following code on the node which you want to run your web server
(Currently webserver tries to insert hardcoded values in the db on receiving
 the API call instead of using request Data)
1.) node clientServer.js 6 tcp://172.0.0.1 12345



API CALL:- IPADDRESSOFWEBSERVER:3000/pushData


This project is based on the raft implementation present at https://github.com/albertdb/Raft.

The entire code was rewritten into python (Original code was written in nodejs which
we suspect to be better choice than python because of its asynchronous nature)

ZeroMQ (http://zeromq.org/) is used for providing communication



#Strategy
Using RAFT for log replication. 
Each log entry contains the write request by a client. Request contains sufficient 
information to identify the file. State machine operation is to append the request 
data to the identified file.
Reads can be handled by the leader


#Status
Code for supporting the write operation was written.
Currently only leader election is working perfectly. 
We are yet to identify the bug because of which client write is not able to 
propogate to the replica nodes.


