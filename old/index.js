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
		'name' : 'mypc'
		'ipaddress' : '172.18.16.71'
	}
];

var my_name = 'mypc';
var leader_node = 'mypc'

//Listening client requests for data writes (apart from galway girl!)
app.get('/pushData', function(req, res){
  //If not leader node, take chill

  //Else perform the following commandments!
  //1. Notify all followers about the client request (send the data too!) and store their response
  //2. If majority of the followers didn't responded take chill!
  //3. Else write the client data into this node and ask followers to do the same.

});


io.on('connection', function(socket){
  socket.on('chat message', function(msg){
    io.emit('chat message', msg);
  });
});
    

http.listen(3000, function(){
  console.log('listening on *:3000');
});