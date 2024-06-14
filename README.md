Deploy on ec2

for deploying into an ec2 instance, I had to install docker and docker-compose on the instance.
```
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt install docker-compose
```


 I also had to open the port 8080,8000,8001 on the instance in the aws console.


I had to clone the repo into the instance and then run the following commands:


```bash
git clone https://github.com/Victor1Ja/harbour-2024-sample.git
docker-compose up -d
```
This runs 2 instances of the app, one on port 8000 and the other on port 8001, a load balancer is used to distribute the load between the two instances hosted on 8080, a mysql database is also running on the instance, and a redis instance is running on the instance.

Only by running the above command, the app is up and running.

make request to instance:8080/hello to see the app running, some times will redirect to instance:8000/hello and some times to instance:8001/hello

