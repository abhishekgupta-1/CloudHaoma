var list_nodes = [
	{
		'name' : 'pc20',
		'ipaddress' : 'https://172.18.16.45'
	},
	{
		'name' : 'mypc',
		'ipaddress' : 'https://172.18.16.71'
	}
];

var port_no = '3000';
var my_name = 'mypc';
var leader_node = 'mypc'

//Following line hardcoded just to save time
//TODO: Loop over list_nodes
var leader_ipaddress = "http://172.17.28.28"+":"+port_no;


const io = require('socket.io-client');
var socket = io(leader_ipaddress);

var pending = [];
var data_dict = {};

socket.on('DataPush', function(msg){
	console.log("Request received with data : "+ msg['data'] + "and requestID = " + msg['requestID']);
	data_dict[msg['requestID']] = msg['data'];
	socket.emit('Acknowledgement', {'data' : 'aye', 'requestID':msg['requestID']});
});

socket.on('DataPushCommit', function(msg){
	console.log("Write final for requestID : " + msg['requestID']);
	console.log("Data : " + data_dict[msg['requestID']] + " writtern!");
});

//Hey, Follower is connected to the leader

