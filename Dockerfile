FROM centos:centos6
MAINTAINER 'ARASHI, Jumpei'
RUN yum install -y python-pip python-setuptools python-devel gcc git
RUN git clone https://github.com/JumpeiArashi/SimpleStepper.git
RUN cd SimpleStepper && python setup.py install
ADD config.py /opt/config.py
EXPOSE 8080
CMD python SimpleStepper/simple_stepper.py --config_file=/opt/config.py
