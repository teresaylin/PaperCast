import socket
import urllib, urllib2

TCP_IP = '18.111.95.199'
TCP_PORT = 80
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
message = "hi"
mydata = [('one', '1'), ('two', '2')]
mydata = urllib.urlencode(mydata)
path = "http://18.111.95.199/index.php"
s.send(message)
s.close()
