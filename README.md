VoIP is a great alternative over the present telephony system. Here, I designed a small project for an emergency protocol using
SIP. I used an asterisk server for this purpose.
The flow through of this model is: 
When an outisder calls 555, the dispatcher types the place where it demands an
emergency service by listening to the outsider. The firstClient script calculates the latitude and longitude of that place
and sends them to the server. The server then finds out the nearest branch from a database corresponding to that location and sends the location,
the call details of that call from Master.csv file and the recording of that same call. All of these are done using sockets.
So there are two sets of clients. One, which does the sending of the location of the place and the branch which takes actions.
