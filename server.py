import SimpleHTTPServer
import SocketServer
from process import main, getVariables
from threading import Timer

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(s):
    (bpmCalibrated, calibrated, realBPM, awakeAvgCalculated, awakeAvg, image_processed, sanitized_str) = getVariables()
    print 'cb: ' + str(bpmCalibrated)
    """Respond to a GET request."""
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    if bpmCalibrated and calibrated:
      s.wfile.write("BPM: " + str(realBPM) + "<br>")
    else:
      s.wfile.write("BPM: NOT CALIBRATED YET" + "<br>")
    if awakeAvgCalculated:
      s.wfile.write("Average awake heart rate: " + str(awakeAvg) + "<br>")
    s.wfile.write("Image processed: " + str(image_processed) + "<br>")
    if image_processed:
      encoded_str = sanitized_str.encode('utf-8')
      print "encoded string"
      s.wfile.write("Reading text: " + encoded_str)

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


