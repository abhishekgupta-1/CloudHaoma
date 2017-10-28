var socketio = document.createElement("script");
socketio.addEventListener("load", proceed1);
socketio.src = "//socket.io/socket.io.js"
function proceed1(){
  var jq = document.createElement("script");
  jq.addEventListener("load", proceed); // pass my hoisted function
  jq.src = "https://code.jquery.com/jquery-1.11.1.js";
}


function proceed () {
  // jQuery load complete, do your magic
  $(function () {
    var socket = io();
    $('form').submit(function(){
      socket.emit('chat message', $('#m').val());
      $('#m').val('');
      return false;
    });
    socket.on('chat message', function(msg){
      $('#messages').append($('<li>').text(msg));
    });
  });

}

 