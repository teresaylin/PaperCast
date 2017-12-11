import SimpleHTTPServer
import SocketServer
from process import main, getVariables
from threading import Timer

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(s):
    (bpmCalibrated, calibrated, realBPM, awakeAvgCalculated, awakeAvg, image_processed, sanitized_str, lastStateAwake) = getVariables()
    print 'cb: ' + str(bpmCalibrated)
    """Respond to a GET request."""
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<h1><strong>BPM: </strong></h1>")
    if bpmCalibrated and calibrated:
      s.wfile.write("<h1 style='color:red'>" + str(realBPM) + "</h1>")
    else:
      s.wfile.write("<h1 style='color:gray'>Not calibrated" + "</h1>")
    s.wfile.write("<h1><strong>Average awake heart rate: </strong></h1>")
    if awakeAvgCalculated:
      s.wfile.write("<h1 style='color:red'>" + str(awakeAvg) + "</h1>")
    
    s.wfile.write("<h1><strong>Status of reader: </strong></h1>")
    if lastStateAwake:
      s.wfile.write("<h1 style='color:red'>Awake</h1>")
    else:
      s.wfile.write("<h1 style='color:red'>Asleep</h1>")
    if image_processed:
      encoded_str = sanitized_str.encode('utf-8')
      print "encoded string"
      s.wfile.write("<h1><strong>Reading text: </strong></h1>")
      s.wfile.write("<p style='color:darkgreen;font-size: large;'>" + encoded_str + "</p>")

Handler = MyRequestHandler
server = SocketServer.TCPServer(('192.168.43.152', 8000), Handler)
print "connected to server"
t = Timer(5, main)
t.start()

try:
	server.serve_forever()
except KeyboardInterrupt:
	server.shutdown()
	server.server_close()
  	print "keyboard interrupt"
	pass


