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
    s.wfile.write("<center><h1 style='font-size: 72pt; font-family:verdana;'><strong>PaperCast </strong><h1></center>")
    s.wfile.write("<center><h2 style='font-size: 36pt; font-family:verdana;'><strong>BPM: </strong></h2></center>")
    if bpmCalibrated and calibrated:
      s.wfile.write("<center><h2 style='font-size: 36pt; color: #bc3451; font-family:verdana;'><strong>"+ str(realBPM)+"</strong></h2></center>")
    else:
      s.wfile.write("<center><h2 style='font-size: 36pt; color: #aaaaaa; font-family:verdana;'><strong>Not Calibrated</strong></h2></center>")
    s.wfile.write("<center><h2 style='font-size: 36pt; font-family:verdana;'><strong>Average Awake Heart Rate: </strong></h2></center>")
    if awakeAvgCalculated:
      s.wfile.write("<center><h2 style='font-size: 36pt; color: #bc3451; font-family:verdana;'><strong>" + str(awakeAvg) +" </strong></h2></center>")

    s.wfile.write("<center><h2 style='font-size: 36pt; font-family:verdana;'><strong>Status of Reader:</strong></h2></center>")
    if lastStateAwake:
      s.wfile.write("<center><h2 style='font-size: 36pt; color: #bc3451; font-family:verdana;'><strong>Awake</strong></h2></center>")
    else:
      s.wfile.write("<center><h2 style='font-size: 36pt; color: #bc3451; font-family:verdana;'><strong>Asleep</strong></h2></center>")
    if image_processed:
      encoded_str = sanitized_str.encode('utf-8')
      print "encoded string"
      s.wfile.write("<center><h2 style='font-size: 36pt; font-family:verdana;'><strong>Text: </strong></h2></center>")
      s.wfile.write("<justified><p style='font-size: 12pt; color: #111111; font-family:verdana; margin: 0px 100px 100px 100px;'>"+encoded_str+"</p></justified>")

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
