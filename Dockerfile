FROM centos:centos6
MAINTAINER 'ARASHI, Jumpei'
RUN yum install -y nodejs npm python-pip python-setuptoos git
RUN git clone https://github.com/JumpeiArashi/SimpleStepper.git
RUN cd SimpleStepper/webui && python setup.py --develop
ADD config.py /opt/config.py
RUN cd SimpleStepper/webui && python simple_stepper.py --config_path=/opt/config.py
