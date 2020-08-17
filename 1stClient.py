import json
import threading
import googlemaps
import sys
import socket
import selectors
import types

messages = []
lat=0.0
lng = 0.0

API_key ='Your api key here' # enter your api key here
gmaps = googlemaps.Client(key=API_key)

def search():
    while True:
        place = str(input()) #despatcher should type the place of incident after hearing it from the caller to find its location
        location = gmaps.geocode(place).json()
        lat = location['geometry']['lat']
        lng = location['geometry']['lng']
        messages.append([lat,lng])


    
# no need size of sending sock as we have two double data types

sel = selectors.DefaultSelector()
t1 = threading.Thread(target=search)
t1.start()



def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1:3]
server_addr = (host, port)
print("starting connection to ", server_addr)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect_ex(server_addr)
print("connected to ", server_addr)
events = selectors.EVENT_WRITE
data = types.SimpleNamespace(
        messages=list(messages),
        outb=b"",
    )
sel.register(sock, events, data=data)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
    sock.close()
