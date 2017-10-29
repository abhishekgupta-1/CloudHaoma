//SocketIO SocketIO SocketIO


var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);


var list_nodes = [
	{
		'name' : 'pc20',
		'ipaddress' : '172.18.16.45'
	},
	{
		'name' : 'mypc',
		'ipaddress' : '172.18.16.71'
	}
];


var my_name = 'mypc';
var leader_node = 'mypc'
var total_nodes = list_nodes.length;
var majority = 2;
//Listening client requests (apart from Galway girl!)
accept_dict = array();

app.get('/pushData', function(req, res){
  //If not leader node, take chill
  if (my_name != leader_node) {
  	//Forward the request to the leader_node
  }
  else {
	//Else perform the following commandments!
	//1. Notify all followers about the client request (send the data too!) and store their response
	//2. If majority of the followers didn't responded take chill!
	//3. Else write the client data into this node and ask followers to do the same.

  	var request_id = Math.random().toString(36).substring(7); //Assigning a randomID
  	console.log("RequestID assigned : " + request_id)
  	//Server sends a write request with requestID to all followers using event 'DataPush'
  	//Server then waits for the events with id = requestID
  	accept_dict[request_id] = 0;
  	io.emit('DataPush', {'data' : '123', 'requestID' : request_id});

  }
  res.send("{'Status' : 'Success'}");
});

//Hey, a follower just connected to me
io.on('connection', function(socket){	
  console.log("Hola, says a follower!");
  #Client sends a Acknowledgement
  socket.io('Acknowledgement', function(msg){
  	request_id = msg['requestID'];
  	accept_dict[request_id] += 1;
  	if (accept_dict[request_id] == majority){
  		io.emit('DataPushCommit', {'requestID' : requestID});
  	}
  }
});
    

//Start http server
http.listen(3000, function(){
  console.log('listening on *:3000');
});