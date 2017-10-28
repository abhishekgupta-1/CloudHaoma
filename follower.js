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

socket.on('DataPush', function(msg){

	console.log(msg['data'])
//	http://172.18.16.71:3000/
});

//Hey, Follower is connected to the leader

