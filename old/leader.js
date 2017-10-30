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
//Listening client requests
var accept_dict = [];

app.get('/pushData', function(req, res){
  //If not leader node, take chill
  if (my_name != leader_node) {
  	//Forward the request to the leader_node
  }
  else {
	//Else perform the following commandments!
	//1. Notify all followers about the client request (send the data too!) and store their response
	//2. If majority of the followers didn't responded do nothing
	//3. Else write the client data into this node and ask followers to do the same.

  	var request_id = Math.random().toString(36).substring(7); //Assigning a randomID
  	console.log("RequestID assigned : " + request_id)
  	//Server sends a write request with requestID to all followers using event 'DataPush'
  	//Server then waits for the events with id = requestID
  	accept_dict[request_id] = 0;
  	io.emit('DataPush', {'data' : '123', 'requestID' : request_id});
  	// var time_out = 1000000;
    var my_int =   setInterval(function(){
    	// console.log(accept_dict[request_id])
      if (accept_dict[request_id] >= majority)
      	res.send("Emitted!");
        clearInterval(my_int);
    },100);
    // while (time_out && accept_dict[request_id]<majority) time_out--;
  	return;
  }
  res.send("{'Status' : 'Success'}");
});




// a follower connected to me
io.on('connection', function(socket){	
  console.log("Hola, says a follower!");
  
  //Client sends a Acknowledgement
  socket.on('Acknowledgement', function(msg){
  	request_id = msg['requestID'];
  	accept_dict[request_id] += 1;
  	if (accept_dict[request_id] == majority){
  		console.log("I am here\n" + accept_dict[request_id])
  		io.emit('DataPushCommit', {'requestID' : request_id});
  	}
  });

});
    

//Start http server
http.listen(3000, function(){
  console.log('listening on *:3000');
});