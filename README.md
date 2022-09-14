# Flask My Ip

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


### Create Crontab
```bash
sudo mkdir /var/log/ip_update/
sudo chown tm:tm /var/log/ip_update/
touch /var/log/ip_update/update.log
python3 update_cf.py >> /var/log/ip_update/update.log 2>&1
```
<hr/>

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

# The creation of the container is in development :raised_back_of_hand:
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
docker build -t chephei/flaskmyip:1.1 .
```
