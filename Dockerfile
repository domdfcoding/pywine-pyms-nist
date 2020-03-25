FROM tobix/pywine
MAINTAINER Dominic Davis-Foster "dominic@davis-foster.co.uk"

ARG BUILD_DATE
ARG VCS_REF

LABEL \
  org.label-schema.build-date=$BUILD_DATE \
  org.label-schema.license="MIT" \
  org.label-schema.name="Docker PyMassSpec NIST Search Flask server" \
  org.label-schema.vcs-url="https://github.com/webcomics/pywine"

COPY pynist_search_server.py /pynist_search_server.py

# Install flask and cheroot for server, plus pyms_nist_search
RUN umask 0 && xvfb-run sh -c "\
  wine pip install --no-warn-script-location flask cheroot pyms-nist-search; \
  wineserver -w"

# Run pynist_search_server
ENTRYPOINT sh -c 'wine py pynist_search_server.py'
