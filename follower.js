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
var leader_ipaddress = "http://172.18.16.71"+":"+port_no;


const io = require('socket.io-client');
var socket = io(leader_ipaddress);

var pending = array();
var data_dict = {};

socket.on('DataPush', function(msg){
	console.log("Request received with data : "+ msg['data'] + "and requestID = " + msg['requestID']);
	data_dict[msg['requestID']] = msg['data'];
	socket.emit(msg['requestID'], {'data' : 'aye', 'requestID':msg['requestID']});
});

//Hey, Follower is connected to the leader

