# busapp209
Bus app for Singaporeans

Usage of the application to check the bus timings of the top 5 bus stop within 400m to the users 

Hosted on heroku free tier, created using python telegram bot library 

You can try the bot at telegram : @bus_209_bot , try it only in mobile env 

This repo contains: 

1. App.py -- Where the main bot run 
2. Config.py -- For setting up sensitive password / information configuration 
3. mod.py -- API request to aid App.py
4. Procfile -- Instruction for Heroku to run my App.py 
5. requirements.txt - libraires / modules / packages to download  

## Docker + minicube : 

`eval $(minikube -p minikube docker-env)`

`docker image build . -t "test"`

`docker container run -t test:latest`

## kube : 

env to minicube, user must be in the same env when docker is building ! 

`minikube docker-env`

Apply manifest file configuration 

`kubectl apply -f deployment.yml`

Get all deployments in development namespace

`kubectl get deployments -n development`

Get all pods in development namespace

`kubectl get pods -n development`   

Get all pods logs 

`kubectl logs --tail=100 <pod-name> -n development`

For real time logs of a pod

`kubectl logs -f <podName>`

For ingress (in minicube)

`minikube addons enable ingress`

`kubectl get ingress -n development`   

Tear down of deployments

`kubectl delete -f deployment.yml`
