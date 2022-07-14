FROM python:2.7.8-slim

# modify wsgiref not to open browser and server continuously
# modify wsgiref default app to only show ENVs sourced from http header

RUN sed -i '/jessie-updates/d' /etc/apt/sources.list  # Now archived
RUN apt-get update && apt-get install patch curl python-pip wget -y --force-yes
COPY ./simple_server.patch /usr/local/lib/python2.7/wsgiref/
RUN patch /usr/local/lib/python2.7/wsgiref/simple_server.py /usr/local/lib/python2.7/wsgiref/simple_server.patch

#RUN pip install requests
WORKDIR /tmp
RUN wget \
	https://files.pythonhosted.org/packages/eb/01/c1f58987b777d6c4ec535b4e004a4a07bfc9db06f0c7533367ca6da8f2a6/certifi-2017.4.17-py2.py3-none-any.whl \
	https://files.pythonhosted.org/packages/24/53/f397db567de0aa0e81b211d81c13c41a779f14893e42189cf5bdb97611b2/urllib3-1.21.1-py2.py3-none-any.whl \
	https://files.pythonhosted.org/packages/11/7d/9bbbd7bb35f34b0169542487d2a8859e44306bb2e6a4455d491800a5621f/idna-2.5-py2.py3-none-any.whl \
	https://files.pythonhosted.org/packages/bc/a9/01ffebfb562e4274b6487b4bb1ddec7ca55ec7510b22e4c51f14098443b8/chardet-3.0.4-py2.py3-none-any.whl

RUN pip install /tmp/*.whl

RUN  wget https://files.pythonhosted.org/packages/65/9c/57484d6ac262af20a10b52cd95ebc99843f282342ef008997ef60f9eeb9c/requests-2.16.5-py2.py3-none-any.whl 

RUN pip install /tmp/requests-2.16.5-py2.py3-none-any.whl

# copies lighttpd and its configurations to folder
# copies demo static files
ADD ./lighttpd-1.4.32 /opt/lighttpd/
ADD ./demo /opt/demo/
ADD ./proxy-compromise /opt/proxy-compromise/
EXPOSE 80
CMD /opt/lighttpd/lighttpd-static -f "/opt/lighttpd/lighttpd.conf" 3>&1; \
	python /opt/proxy-compromise/proxy.py;