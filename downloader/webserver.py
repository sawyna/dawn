from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import urllib
import sys
import re
import json
import traceback
from config import dbconfig
from yt_downloader import YTDownloader

class MyRequestHandler(BaseHTTPRequestHandler):

	download = re.compile("^download")
	status = re.compile("^status")

	"""docstring for WebServer"SimpleHTTPServer.SimpleHTTPRequestHandler"""
	def __init__(self, request, client_address, server):
		BaseHTTPRequestHandler.__init__(self, request, client_address, server)

	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self.end_headers()

	def get_query_params(self):
		path = str(self.path)
		temp_list = str(path).split("?")
		sz = len(temp_list)
		params = {}
		if(sz > 1):
			queryParamsString = temp_list[1]
			queryParams = str(queryParamsString).split("&")
			for queryParam in queryParams:
				temp_list = queryParam.split("=")
				if(len(temp_list) > 1):
					params[temp_list[0]] = urllib.unquote(temp_list[1])
		return params


	def start_download(self, params):
		YTDownloader(dbconfig).download(params)


	def send_status(self, params):
		return YTDownloader(dbconfig).get_status(params)

	def do_GET(self):
		print threading.currentThread().getName()
		response = {}
		path = str(self.path)[1:]
		params = self.get_query_params()
		try:
			if self.download.match(path):
				response['payload'] = self.start_download(params)
				self.send_response(200)
			elif self.status.match(path):
				response['payload'] = self.send_status(params)
				self.send_response(200)
			else:
				print "Forbidden"
				self.send_response(403)				

		except Exception, err:
			traceback.print_exc()

			response['payload'] = {"error": "unexpected error"}
			self.send_response(500)

		self.end_headers()
		self.wfile.write(json.dumps(response))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"Handle requests in a separate thread"


def start_server():
	args = sys.argv
	PORT = int(args[1])
	httpd = ThreadedHTTPServer(("", PORT), MyRequestHandler)

	print "serving at port", PORT
	httpd.serve_forever()


start_server()