# setup
## prereqs
First install reqs  
```pip install -r requirements.txt```  
Then download nltk corpora  
```./download-vocab.sh```

## env
Create a `.env` file  
it should have the following configurations, TOKEN, CHANNEL_ID, AUTHOR_ID and optionally TEST_CHANNEL_ID, TEST_AUTHOR_ID. An example .env looks like  
```
TOKEN=xxx
CHANNEL_ID=yyy
AUTHOR_ID=zzz
TEST_CHANNEL_ID=aaa
TEST_AUTHOR_ID=bbb
```

# running
you can run simply with `python bot.py` or `python bot.py --test` to run in test mode (uses test channel/ test author)