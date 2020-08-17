import json
import pymysql
from math import radians, sin, cos, acos, fabs
import sys
import socket
import selectors
import types
import tqdm
import os
from datetime import datetime
from datetime import timedelta
import ipaddress
import time
now = datetime.now()
tym = now.strftime("%Y-%m-%d %H:%M:%S")
intranet = {"op1": "100", "op2": "200"}   # username of op1 and op2 as keys and their local numbers as values
branchUser = {"Anna Nagar": "userAnna", "Velachery": "userVela", "Poonamallee": "userPoon", "Nungambakkam": "userNung", "Villivakkam": "userVill", "Kodungaiyur": "userKodu", "Purasaiwakkam": "userPura", "Koyambedu": "userKoya", "T Nagar": "userTnag" }
# save each branch name and its user_name
dispUnmonitored = {"Anna Nagar": [], "Velachery": [], "Poonamallee": [], "Nungambakkam": [], "Villivakkam": [], "Kodungaiyur": [], "Purasaiwakkam": [], "Koyambedu": [], "T Nagar": [] }
# to display unsolved problems.
'''Anna Nagar
Velachery
Poonamallee
Nungambakkam
Villivakkam
Kodungaiyur
Purasaiwakkam
Koyambedu
T Nagar'''


SEPARATOR = ","
header_size = 2


db = pymysql.connect("localhost","username","password","controlRoom")
cursor = db.cursor()
cursor.execute("SELECT latitude,longitude,name FROM branch")
rows = cursor.fetchAll()


def printStatus():
    print (dispUnmonitored)
def findnearest(lat,lng):
    dist=[]
    for row in rows:
        dist.append(6371.01 * acos(sin(row[0])*sin(lat) + cos(row[0])*cos(lat)*cos(row[1] - lng)))
    return row[dist.index(min(fabs((dist))))]

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from ", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", user_name='', recv_len = 0, name=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    user_name = socket.gethostbyaddr(data.addr[0])
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  # Should be ready to read

            if recv_data and user_name in intranet:
                latloc, longloc = recv_data
                LAT,LNG,Name = findnearest(latloc,longloc)
                with open("/var/log/asterisk/cdr-csv/Master.csv", "rb") as f:
                    for line in f:
                        words = line.rsplit(",")
                        if intranet["user_name"] in words and strcmp(words[11],tym)>=0 : #words[11] gives the timestamp of end call
                            data.outb+=line+"\n"+str(latloc)+","+str(longloc)                     # we ll encode it while sending
                            tym = words[11]                                               # get the new tym for parsing the next data.
                with os.scandir(r'/Prem/desktop/intranet["user_name"]/') as files:
                    for i in range(1,len(files)):
                        if strcmp(files[i],tym) >= 0 and strcmp(files[i-1],tym) < 0:
                            break
                    with open(r'/Prem/desktop/intranet["user_name"]/files[i-1].wav','rb') as r:
                        lines = r.readall()
                    data.outb+="\n" + lines +"\n"
                data.user_name=user_name
                data.name=Name
                data.recv_len = len(data.outb)
                dispUnsolved[Name].append(str(latloc)+","+str(longloc)+" "+tym+"\n")


            elif recv_data and user_name not in intranet:
                key_list = list(branchUser.keys())
                val_list = list(branchUser.values())
                del dispUnmonitored[key_list[val_list.index(user_name)]][0]

        except:
            print("closing connection to ", data.addr)
            del online[sock]
            sock.close()
    if mask & selectors.EVENT_WRITE:
        try:

            if data.outb:
                if (user_name == branchUser[data.name]):
                    sent = sock.send((f'{data.recv_len}:<{header_size}'+data.outb[:data.recv_len]).encode())
                    data.outb = data.outb[(sent-header_size):]

        except:
            print("closing connection to ", data.addr)
            del online[sock]
            sock.close()



if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)
host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
try:
    while True:
        printStatus()
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
