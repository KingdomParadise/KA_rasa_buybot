Facebook Automessenfer with custom chatbot API


## Run the Project 

There must be 2 RASA servers Running
```
1.   rasa run actions
```
and 
```
2.  rasa run -m model  --enable-api --cors "*"
```

And a CHROME EXTENSION for testing purpose
 
```
https://chrome.google.com/webstore/detail/clean-all-history-cache-c/elidgjfpciimeeeoeneeiifkmhadhkeh?hl=en
```


<!-- 

## Working
Project folder consists of multiple files and each contributes to a specific functionality.

### main.py

This file is responsible for handling the GUI section of project and also it combines all modules together.

### contact_fetch.py

This file fecthes list of firends determined as maximum contacts to be fetched

### auto_messenger.py

This file handles the chat activity with the users and it reads data from fresh_fetched_contacts.txt to keep track of targetted users.

### api.py

This file is called by auto_messenger.py files and it send request to CHAT_BOT SERVER for a reply.

### credentials.txt

This file is used to store the recent user credentials

### fresh_fetched_contacts.txt

This file is used to store the ids of users determined as maximun contacts to be fetched.



 -->
