docker run \
  -it \
  -p 5001:5001 \
  --name=pyms-nist-server \
  --rm \
  -v "/home/domdf/Python/mainlib/:/mainlib" \
 domdfcoding/pywine-pyms-nist
