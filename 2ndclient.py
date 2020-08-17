import sys
import socket
import selectors
import types
import threading
import ipaddress

sel = selectors.DefaultSelector()
messages = []
header_size = 2

def get_input():
    while True:
        message = input()
        messages.append(message)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(4096)  # Should be ready to read
        if recv_data:
            size = int(recv_data[:header_size])
            recv_data = recv_data[header_size:]
            with open(r'/client/callDetails.txt','a') as f:
                f.write(recv_data[:size])

    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.messages[0] += "\n"
            data.outb = f'{len(data.messages[0])}:<{header_size}' + data.messages.pop(0)
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
events = selectors.EVENT_READ | selectors.EVENT_WRITE
data = types.SimpleNamespace(
        messages=list(messages),
        outb=b"",
    )
sel.register(sock, events, data=data)

thread_input = threading.Thread(target=get_input)
thread_input.start()
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
