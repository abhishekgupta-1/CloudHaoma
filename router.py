import sys
import zmq


# var debug=process.argv[3]=="true",
#     zmq=require('zmq'),
#     router=zmq.socket('router'),
#     snappy = require('snappy');

# router.bindSync('tcp://*:'+process.argv[2]);

# router.on('message',function(){
#     var args = Array.apply(null, arguments);
#     if(debug){
#         var aux=args.slice();
#         if(aux[3]=='c') aux[4]=snappy.uncompressSync(aux[4]);
#         showArguments(aux);
#     }
#     router.send([args[2],'',args[0],args[3],args[4]]);
# });

# //Aux functions
# function showArguments(a) {
# for(var k in a)
# console.log('\tPart', k, ':', a[k].toString());
# };

debug = (sys.argv[2] == "true")
context = zmq.Context()
receiver_socket = context.socket(zmq.PULL)
receiver_socket.bind("tcp://*:"+str(sys.argv[1]))
sender_socket = context.socket(zmq.PUB)
sender_socket.bind("tcp://*:5000");

while True:
	data = receiver_socket.recv_json()
	dest_id = data['dest']
	print data
	sender_socket.send("%d %s"%(dest_id, data))
