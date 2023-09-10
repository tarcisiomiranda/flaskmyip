# Flask My Ip + Bot Telegram
# Installation

Using ***Flaskmyip*** is basically a five-step process:
1. Install dependencies using `pip3`
```
pip3 install -r requirements.txt
```
2. Create a file call `domains.txt` and add the record type and dominion separated by ";".
3. Rename `.env_exemple` to only `.env` then put the necessary credentials to start the program execution.
4. Using the ```--log``` as argument, you can write the application log to the path configured in your `.env`, but by default it is `/var/log/ip_update/update.log`

```
python3 run.py --log
```
5. You can create a cron job, in this case on your linux server (for 5m in 5m run check IP)

***/etc/crontab***
```bash
*/5 *  * * * root cd /folder_path/flaskmyip/; python3 run.py --log
```
<br/>

# For development
## Install using PIP ENV
```
pipenv install
```
<hr/>

## Get a new requirements.txt
```
pip freeze > requirements.txt
```

#### You can convert a Pipfile and Pipfile.lock into a requirements.txt. Take a look into this
```
pipenv lock -r
```
#### After that, you can install all your modules in your python virtual environment by doing the following:
```
pip install -r requirements.txt
```


## DOC CloudFlare to explain PUT and GET of API
***GET***
<a href="https://api.cloudflare.com/#dns-records-for-a-zone-dns-record-details">
DNS Record Details
</a>

***PUT***
<a href="https://api.cloudflare.com/#dns-records-for-a-zone-update-dns-record">
Update DNS Record
</a> 

<hr/>
<br/>
<br/>

## The creation of the container is in development :raised_back_of_hand:
```
app.py
Dockerfile
```

## Teste API
```bash
curl -X GET http://test.api
```

## Build your docker image
```docker
# Build for AMD64
docker build -t registry.tarcisio.me/home/flaskmyip:latest -f docker/Dockerfile_home .

# Build for raspberry FLASK
docker build -t registry.tarcisio.me/home/flaskmyip:armv7l -f docker/Dockerfile_home .

# Build for raspberry NTP
docker build -t registry.tarcisio.me/home/ntp:armv7l -f docker/Dockerfile_ntp .

# Build for raspberry FTPD
docker build -t registry.tarcisio.me/home/ftp:armv7l -f docker/Dockerfile_ftpd .
```

# https://stackoverflow.com/questions/991758/how-to-get-pem-file-from-key-and-crt-files
openssl rsa -in server.key -text > private.pem
# https://docs.paramiko.org/en/stable/api/client.html

# tmux 
setw synchronize-panes


# isntall dep
pip3 install paramiko


# GPG
- https://medium.com/@almirx101/pgp-key-pair-generation-and-encryption-and-decryption-examples-in-python-3-a72f56477c22


# AWS CLI
***AIM***
AKIA3EFLTVJD3567QKOY
9sWIdTN2wzRN2a+xvPV8RjPJCvmNUhvxmRkfmOsC


# AWS isntall CLI
***Linux_x64***
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && \
sudo ./aws/install
```

***Linux_arm64***
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && \
sudo ./aws/install
```

## Lib da autenticação dois passos
```
pip install pyotp
```
