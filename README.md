# Flask My Ip + Bot Telegram
# Installation

Using Docker Compose is basically a three-step process:
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
docker build -t chephei/flaskmyip:1.1 .
```
