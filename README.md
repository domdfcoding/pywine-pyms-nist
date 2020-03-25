# pywine-pyms-nist

## Docker container for the Flask search server for PyMassSpec NIST Search

This is a docker container to allow PyMassSpec NIST Search to function on Linux via a Flask REST API. It is based on the [pywine](https://hub.docker.com/r/tobix/pywine) docker image by [webcomics](https://github.com/webcomics).

This container isn't designed to be run directly; rather it is invoked automatically from [PyMassSpec NIST Search](https://github.com/domdfcoding/pynist) when running on platforms other than Windows. 