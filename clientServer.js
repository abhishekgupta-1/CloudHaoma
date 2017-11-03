//node clientServer.js 2 tcp://172.0.0.1 12345

serverID = process.argv[2]
router_address = process.argv[3]
send_port_no = process.argv[4]
 // serverID = process.argv[5];
var app = require('express')();
var http = require('http').Server(app);
var zmq = require('zmq');


listen_socket = zmq.socket('pull');
listen_socket.connect(router_address+":5002")

sender_socket = zmq.socket('push')
sender_socket.connect(router_address+":"+send_port_no)

listen_socket.on('message', function(){
  console.log("here\n")
  var args = Array.apply(null, arguments);
  console.log(args[0].toString('utf8'));
  var message = JSON.parse(args[0].toString('utf8'))
  console.log(message);
  accept_dict[message['requestId']] = message['status'];
});

// data = {'dest':1}
// i = 5;
// function send_mess(){
//   console.log("here")
//   sender_socket.send(JSON.stringify(data)); 
//   if (i!=0)
//     setTimeout(send_mess, 500);
//   i--;
// }
// send_mess();

var accept_dict = [];
var counter = 0;

app.get('/pushData', function(req, res){
	var request_id = Math.random().toString(36).substring(7); //Assigning a randomID
	console.log("RequestID assigned : " + request_id)
	accept_dict[request_id] = 'failure';
  counter += 1
  msg = {'clientId':serverID
  , 'dest': 1
  , 'requestId' : request_id
  , 'request_data' : {'data':'123'+counter, 'fileName': 'abc' + counter }
  , 'rpc':'addEntry'
  };

  sender_socket.send(JSON.stringify(msg));
	console.log("here")
  //io.emit('DataPush', {'data' : '123', 'requestID' : request_id});
	// var time_out = 1000000;
  var count = 20;
  var my_int =   setInterval(function(){
   if (count == 0) {
    res.send("Not added!")
    clearInterval(my_int)
    return
   }
   if (accept_dict[request_id] == "Success"){
    	console.log("Log accepted");
      res.send("Log added!");
      clearInterval(my_int);
    }
  },100);
  // while (time_out && accept_dict[request_id]<majority) time_out--;
	return;
});



//Start http server
http.listen(3000, function(){
  console.log('listening on *:3000');
});