FROM tobix/pywine
MAINTAINER Dominic Davis-Foster "dominic@davis-foster.co.uk"

ARG BUILD_DATE
ARG VCS_REF

LABEL \
  org.label-schema.build-date=$BUILD_DATE \
  org.label-schema.license="MIT" \
  org.label-schema.name="Docker PyMassSpec NIST Search Flask server" \
  org.label-schema.vcs-url="https://github.com/domdfcoding/pywine-pyms-nist"

COPY search_server.py /search_server.py
COPY requirements.txt /requirements.txt
COPY templates/ /templates/

# Install dependencies
RUN umask 0 && xvfb-run sh -c "\
  wine pip install --no-warn-script-location -r requirements.txt; \
  wineserver -w"

ENV PYTHONUNBUFFERED=1

# Run pynist_search_server
ENTRYPOINT export LIBTYPE && sh -c 'wine py search_server.py'
