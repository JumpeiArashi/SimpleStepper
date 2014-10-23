FROM centos:centos6
MAINTAINER 'ARASHI, Jumpei'
RUN yum install -y nodejs npm python-pip python-setuptools git
RUN git clone https://github.com/JumpeiArashi/SimpleStepper.git
RUN npm install bower grunt-cli 
RUN cd SimpleStepper/webui && grunt build
RUN cd SimpleStepper && python setup.py develop
ADD config.py /opt/config.py
EXPOSE 8080
CMD python SimpleStepper/simple_stepper.py --config_file=/opt/config.py
