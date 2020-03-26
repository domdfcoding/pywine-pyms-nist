#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  pynist_search_server.py
#

# stdlib
import json

# 3rd party
from flask import Flask, request
from pyms.Spectrum import MassSpectrum
from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher

import pyms_nist_search
from pyms_nist_search.json import PyNISTEncoder

app = Flask(__name__)

# Setup pyms_nist_search
FULL_PATH_TO_MAIN_LIBRARY = "Z:\\mainlib"
FULL_PATH_TO_WORK_DIR = "Z:\\root"


try:
	search = pyms_nist_search.Engine(FULL_PATH_TO_MAIN_LIBRARY, pyms_nist_search.NISTMS_MAIN_LIB, FULL_PATH_TO_WORK_DIR)
	
	status_message = "ready"
	status_code = 200
	
except ValueError as e:
	search = None
	
	status_message = str(e)
	status_code = 500


@app.route("/", methods=['GET'])
def status():
	return status_message, status_code


@app.route("/search/quick/", methods=['POST'])
@app.route("/search/quick", methods=['POST'])
def quick_search():
	print("Searching Spectrum (Quick Search)")
	
	if search is None:
		return status()
	
	ms = MassSpectrum(**json.loads(request.get_json()))
	hit_list = search.spectrum_search(ms)
	return json.dumps(hit_list, cls=PyNISTEncoder)


@app.route("/search/spectrum/", methods=['POST'])
@app.route("/search/spectrum", methods=['POST'])
def spectrum_search():
	print("Searching Spectrum")
	
	if search is None:
		return status()
	
	ms = MassSpectrum(**json.loads(request.get_json()))
	hit_list = search.full_spectrum_search(ms)
	return json.dumps(hit_list, cls=PyNISTEncoder)


@app.route("/search/spectrum_with_ref_data/", methods=['POST'])
@app.route("/search/spectrum_with_ref_data", methods=['POST'])
def spectrum_search_with_ref_data():
	print("Searching Spectrum with Ref Data")
	
	if search is None:
		return status()
	
	ms = MassSpectrum(**json.loads(request.get_json()))
	hit_list = search.full_spectrum_search(ms)
	output_buffer = []
	
	for idx, hit in enumerate(hit_list):
		ref_data = search.get_reference_data(hit.spec_loc)
		output_buffer.append((hit, ref_data))
	
	return json.dumps(output_buffer, cls=PyNISTEncoder)


@app.route("/search/loc/<int:loc>", methods=['GET', 'POST'])
def loc_search(loc):
	print("Getting Reference Data")
	
	if search is None:
		return status()
	
	x = search.get_reference_data(loc)
	# print(request.data)
	return json.dumps(x, cls=PyNISTEncoder)


# if __name__ == "__main__":
# 	app.run(debug=True, host="0.0.0.0", port=5001)

if __name__ == '__main__':
	d = WSGIPathInfoDispatcher({'/': app})
	server = WSGIServer(('0.0.0.0', 5001), d)
	
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()
