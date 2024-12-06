# **Telred**
Bot that performs seamless repost of reddit submissions into telegram chat

## **Installing telred**

1. Download repo
```shell
git clone https://github.com/Dreadyyyy/telred
```
2. Change directory
```shell
cd telred
```
## **Running telred with python**

1. Create virtual environment
```shell
python -m venv .venv
```

2. Activate virtual environment
```shell
source .venv/bin/activate
```

3. Install dependencies
```shell
pip install -r requirements.txt
```

4. Create .env file with credentials
```shell
echo BOT_TOKEN=your_api_token>>.env
echo CLIENT_ID=your_reddit_client_id>>.env
echo CLIENT_SECRET=your_reddit_client_secret>>.env
echo USER_AGENT=your_reddit_user_agent>>.env
```

5. Run bot
```shell
python main.py
```
## **Running telred with docker**

1. Build docker image
```shell
docker build . -t telred:latest                             
```
2. Create .env file with credentials
```shell
echo BOT_TOKEN=your_api_token>>.env
echo CLIENT_ID=your_reddit_client_id>>.env
echo CLIENT_SECRET=your_reddit_client_secret>>.env
echo USER_AGENT=your_reddit_user_agent>>.env
```
3. Run the container
```shell
docker run -p 8080:8080 -v "$(pwd)/.env":/.env telred  
```
