# busapp209
Bus app for Singaporeans

Usage of the application to check the bus timings of the top 5 bus stop within 400m to the users 

You can try the bot at telegram : @bus_209_bot , try it only in mobile env 

This repo contains: 

1. App.py -- Where the main bot run 
2. Config.py -- For setting up sensitive password / information configuration 
3. mod.py -- API request to aid App.py
4. Procfile -- Instruction for Heroku to run my App.py 
5. requirements.txt - libraires / modules / packages to download  

# How to run locally 

pre req : 
--> python version : 3.11 
--> any linux env  

## install virtual env 
sudo apt install python3-virtualenv
source venv/bin/activate
pip install -r requirements.txt
python app.py

