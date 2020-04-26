#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  pynist_search_server.py
#

# stdlib
import json
import os
import pkgutil
import sys

# 3rd party
import cheroot
import flask
import pyms
import pyms_nist_search
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher, Server as WSGIServer
from pyms.Spectrum import MassSpectrum
from pyms_nist_search.json import PyNISTEncoder
from stdlib_list import stdlib_list

__author__ = 'Dominic Davis-Foster'
__license__ = 'MIT'
__maintainer_email__ = 'dominic@davis-foster.co.uk'
__version__ = '0.1.1'

__copyright__ = "2020 Dominic Davis-Foster"
__email__ = "dominic@davis-foster.co.uk"


app = flask.Flask(__name__)

# Setup pyms_nist_search
FULL_PATH_TO_MAIN_LIBRARY = "Z:\\mainlib"
FULL_PATH_TO_WORK_DIR = "Z:\\root"

LIB_TYPE = int(os.environ.get("LIBTYPE"))
if not LIB_TYPE:  # i.e. environment variable was unset. 0 isn't a valid value either
	lib_type = pyms_nist_search.NISTMS_MAIN_LIB
	
try:
	search = pyms_nist_search.Engine(FULL_PATH_TO_MAIN_LIBRARY, LIB_TYPE, FULL_PATH_TO_WORK_DIR)
	
	status_message = "ready"
	status_code = 200

except (ValueError, FileNotFoundError) as e:
	search = None
	
	status_message = str(e)
	status_code = 500


@app.route("/", methods=['GET'])
def status():
	return status_message, status_code


@app.route("/info", methods=['GET'])
def info():
	# TODO: Replace with pretty HTML page
	
	package_list = []
	
	buffer = []
	
	stdlib_libraries = stdlib_list()
	builtin_libraries = list(sys.builtin_module_names)
	exclude_libraries = stdlib_libraries + builtin_libraries + ["this"]
	
	for path, pkg, ispkg_flag in pkgutil.iter_modules(None):

		if str(path).endswith("DLLs')"):
			continue
			
		if pkg not in exclude_libraries and not pkg.startswith("_"):
			buffer.append(pkg)
			if len(buffer) == 5:
				package_list.append(buffer)
				buffer = []
	
	if buffer:
		package_list.append(buffer)
	
	return flask.render_template(
			"info.html",
			package_list=package_list,
			pywine_pyms_nist_version=__version__,
			pyms_nist_search_version=pyms_nist_search.__version__,
			pyms_version=pyms.__version__,
			flask_version=flask.__version__,
			cheroot_version=cheroot.__version__,
			python_version=sys.version,
			)


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
	# 	app.run(debug=True, host="0.0.0.0", port=5001)
	
	d = WSGIPathInfoDispatcher({'/': app})
	server = WSGIServer(('0.0.0.0', 5001), d)
	
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()
