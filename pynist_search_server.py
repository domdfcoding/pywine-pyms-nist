#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  pynist_search_server.py
#

# stdlib
import json

# 3rd party
import pyms
import pyms_nist_search
import cheroot
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher, Server as WSGIServer
import flask
from pyms.Spectrum import MassSpectrum
from pyms_nist_search.json import PyNISTEncoder

app = flask.Flask(__name__)

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


@app.route("/info", methods=['GET'])
def info():
	# TODO: Replace with pretty HTML page
	return f"""pynist_search_server info

	PyMassSpec NIST Search version {pyms_nist_search.__version__}

	PyMassSpec version {pyms.__version__}")

	Flask version {flask.__version__}

	Cheroot version {cheroot.__version__}

"""

@app.route("/search/quick/", methods=['POST'])
@app.route("/search/quick", methods=['POST'])
def quick_search():
	print("Searching Spectrum (Quick Search)")
	
	if search is None:
		return status()
	
	n_hits = flask.request.args.get('n_hits', default=5, type=int)
	
	ms = MassSpectrum(**json.loads(flask.request.get_json()))
	hit_list = search.spectrum_search(ms, n_hits)
	return json.dumps(hit_list, cls=PyNISTEncoder)


@app.route("/search/spectrum/", methods=['POST'])
@app.route("/search/spectrum", methods=['POST'])
def spectrum_search():
	print("Searching Spectrum")
	
	if search is None:
		return status()
	
	n_hits = flask.request.args.get('n_hits', default=5, type=int)
	
	ms = MassSpectrum(**json.loads(flask.request.get_json()))
	hit_list = search.full_spectrum_search(ms, n_hits)
	return json.dumps(hit_list, cls=PyNISTEncoder)


@app.route("/search/spectrum_with_ref_data/", methods=['POST'])
@app.route("/search/spectrum_with_ref_data", methods=['POST'])
def spectrum_search_with_ref_data():
	print("Searching Spectrum with Ref Data")
	
	if search is None:
		return status()
	
	n_hits = flask.request.args.get('n_hits', default=5, type=int)
	
	ms = MassSpectrum(**json.loads(flask.request.get_json()))
	hit_list = search.full_spectrum_search(ms, n_hits)
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
	# print(flask.request.data)
	return json.dumps(x, cls=PyNISTEncoder)


if __name__ == "__main__":
	# print("pynist_search_server info:")
	# print(f"	 PyMassSpec NIST Search version {pyms_nist_search.__version__}")
	# print(f"	 PyMassSpec version {pyms.__version__}")
	
# 	app.run(debug=True, host="0.0.0.0", port=5001)

	d = WSGIPathInfoDispatcher({'/': app})
	server = WSGIServer(('0.0.0.0', 5001), d)
	
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()
