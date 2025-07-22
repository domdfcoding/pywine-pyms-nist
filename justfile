default: lint

unused-imports:
	tox -e lint -- --select F401

incomplete-defs:
	tox -e lint -- --select MAN

bare-ignore:
	greppy '# type:? *ignore(?!\[|\w)' -s

lint: unused-imports incomplete-defs bare-ignore
	tox

build:
  docker build --no-cache -t domdfcoding/pywine-pyms-nist .
