SimpleStepper
=============

![Circle CI build status](https://circleci.com/gh/JumpeiArashi/SimpleStepper.svg?style=shield&circle-token=:73be2d63d115ec3560d8efb69139562d482197bd)


What is **SimpleStepper** ?
-----------------------------

Our SimpleStepper simplifies your AWS resources access with HTTP request.
SimpleStepper is consisted [AngularJS](https://angularjs.org/), [Tornado](http://www.tornadoweb.org/en/stable/) and [Docker](https://www.docker.com/).
When SimpleStepper received HTTP POST request, SimpleStepper backend system called AWS EC2 API(security group API).
And backend system add cut-and-dried inbound(ingress) rules to specified security groups.
Allowed IP address of inbound rules is your source IP address.

note:

If `X-Forwarded-For` header includes in request headers, SimpleStepper use the value as source IP to make an opening into security group.
This means that you are able to run SimpleStepper behind some reverse proxy(ELB, nginx or HAProxy).


Getting Start
-------------

1. Install docker-io
2. Clone SimpleStepper
3. Configure your security group defines
4. Launch your SimpleStepper
5. Add your inbound rules

### Install docker-io

First, you need to install `docker-io` to launch easily SimpleStepper.

```bash
sudo yum install docker-io
sudo /etc/init.d/docker start
```

### Clone SimleStepper

Clone SimpleStepper source code to get base Dockerfile.

```bash
git clone https://github.com/JumpeiArashi/SimpleStepper.git
```

### Configure your security group defines

See the below sample settings.

```python
port = 8080
region_name = 'AWS_REGION_NAME'
aws_access_key_id = 'YOUR_AWS_ACCESS_KEY_ID'
aws_secret_access_key = 'YOUR_AWS_SECRET_ACCESS_KEY'
security_group_defines = {
    'sg-XXXXXXXX': [
        {'tcp': 22},
        {'tcp': 80}
    ],
    'sg-YYYYYYYY': [
        {'tcp': 3306},
        {'udp': 11211}
    ]
}
```

#### port

Listen port of SimpleStepper.

e.g:

```
port = 8080
```

#### region_name

This parameter is AWS region where your security groups exists.

e.g

```
region_name = 'us-east-1'
```

#### aws_access_key_id

Your AWS Access Key ID.

#### aws_secret_access_key

Your AWS Secret Access Key.

#### security_group_defines

Your security group ID and port that you want to allow  mapping.
This parameter must be a python dict type object that has below struct.

```python
{
    'SECURITY_GROUP_ID': [
         {PROTOCOL: PORT_NUMBER}
     ]
}
```

e.g

```python
{
    'sg-abc12345': [
        {'tcp': 22},
        {'tcp': 3306}
    ],
    'sg-12345abc': [
        {'udp': 11211}
    ]
}
```

### Launch your SimpleStepper

In previous section, you have just completed your configuration file.
Now, you can build your SimpleStepper.

```bash
cd YOUR_SIMPLE_STEPPER directory
docker build ./ --no-chache=true
```

And run the docker container.

```bash
docker run -i -d -p 8080:8080 CONTAINER_ID
```

### Add your inbound rules

Finally you can add inbound rules with just one-click!!
Let's access your SimpleStepper server and click `Append Your IP!!` button.


API Reference
-------------

SimpleStepper provides below APIs.
All end point has `/api` url as uri prefix.

### /api/inboundRules

#### GET

This API gets your security group rules and returns following json.

```json
{
  "results": [
    {
      "id": "sg-XXXXXXXX",
      "name": "SecurityGroup001",
      "rules": [
        {
          "port": "22 - 22",
          "protocol": "tcp",
          "source": "192.30.252.1/32"
        }
      ]
    }
  ]
}
```

#### POST

Add inbound rules to your specified security group.
POST body must be empty.
So you can use below command(curl) to add your global IP address.

```bash
curl -X POST https://YOUR_SIMPLE_STEPPER_ENDPOINT/api/inboundRules
```

This API returns following json.

```json
{
  "status_code": 200,
  "message": "Your IP GLOBAL_IP is appended to ['SECUTIRY_GROUP_ID_001', 'SECURITY_GROUP_ID_002'...]"
}
```

#### DELETE

Delete all inbound rules of specified security groups and returns following json.

```json
{
  "results": [
    {
      "to_port": 22,
      "from_port": 22,
      "ip_protocol": "tcp",
      "cidr_ip": "192.39.252.1/32"
    }
  ]
}
```

note: Using `DELETE` http method, you can **all** inbound rules of the security group what you specify in `config.py`.


Warning
-------

SimpleStepper has no mechanism of access controlling.
So you may have to access control such as a verification by client certification, ACL by source IP, etc...

FYI: We use SimpleStepper as pseudo-VPN to production environment.
Our verification is by client certification on Nginx.
So we make Nginx reverse proxy.


For developer
--------------

Fork me! And do me pull request!

note:

If you don't like our UI, you can customize and develop with *development mode*.

1. Modify API endpoint in UI.
2. Run SimpleStepper backend system with development mode.
3. Customize SimpleStepper UI.

### Modify API endpoint in UI

Open `webui/app/scripts/services/config.js` file by your favorite editor.
Modify `apiEndpoint` parameter.

```javascript
# before
angular.module('simpleStepperWebuiApp')
  .constant('apiEndpoint', '/api');
# after
angular.module('simpleStepperWebuiApp')
  .constant('apiEndpoint', 'http://localhost:8080/api');
```

### Run SimpleStepper backend system with development mode.

```bash
# In your local PC or development server.

python setup.py develop
python simple_stepper.py --development --config_file=config.py
```

Now, SimpleStepper will listen on `Access-Control-Allow-Origin: *` with using CORS(Cross-Origin Resource Sharing, Allow-Origin is *) when you will specify `--development` option.

### Customize SimpleStepper UI

We created base Model of webui with AngularJS, yaomen.
So you need install to some javascript components.

```
cd webui/app

# Install required npm modules with package.json file
npm install

# Install required bower components with bower.json file
bower install
```

Let's create your SimpleStepper UI.


Future
------

* Creating DEMO page for showing SimpleStepper UI.
* Building own(Oreoreism in Japanese!) certificate authority in docker container.
* Creating client certification by using above CA.
* Run SimpleStepper with Nginx(Include verification by client certification) in docker container.
* Temporary credential by using EC2 instance's IAM role.
* Provide IAM role json that has an authority to modify specified security groups.
* Run SimpleStepper docker container with AWS ElasticBeansTalk.


License
-------

SimpleStepper is released under the [WTFPL license](http://www.wtfpl.net/) ![WTFPL license logo](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png)
