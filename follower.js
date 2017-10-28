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
var leader_ipaddress = "http://172.18.16.71:3000"

const io = require('socket.io-client');
var socket = io(leader_ipaddress);