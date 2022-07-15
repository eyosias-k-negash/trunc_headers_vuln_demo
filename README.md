# trunc_headers_vuln_demo

# about the image
trunc_headers_vuln_demo is a docker image put together to showcase a vulnerability discussed in this link blog.

At the expense of clarity this demo is built in to one image in order to avoid space usage and complexity brought by separate services hosting each component. This image has 3 components listed here and desribed in READMEs they reside in.

- SPA displaying the vulnerability - as per the options set it send a request to a python proxy script through lighttpd proxy
- lighttpd proxy - hosts all components of the demo and is involved in the vulneribility
- a proxy python script - used to send malformed headers as the Javascript in the SPA is not able to do that
- a mock backend wsgi server - A simple python wsgi server where the vunlerability potentially manifests

# getting up and running

Docker service needs to be installed and running.
*This image has not been tested on docker for windows.*

```sh
git clone https://github.com/eyosias-k-negash/trunc_headers_vuln_demo.git
cd trunc_headers_vuln_demo
docker build -t trunc_headers_vuln_demo .
docker run -it -p 80:80 trunc_headers_vuln_demo


## giphy video