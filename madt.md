# Build madt image
```sh
docker build -t madt/kahypar images/kahypar
docker build -t madt .
```


# Run docker container
```sh
sudo docker run --rm -it --name madt --privileged -p 8980:80 -p 8922:22 -v /home/sea1and/dltc/madt/labs:/home/demo/labs -e SSH_PWD=demo -e MADT_RUNTIME=docker -v ~/dltc/madt/madt_ui:/app --entrypoint ash madt
```

# Run next commands inside container
```sh
dockerd --oom-score-adjust 500 --log-level error > /home/demo/docker.log 2>&1 &
sh /home/demo/images/build.sh

(or)
dockerd --oom-score-adjust 500 & sh /home/demo/images/build.sh

docker build -t madt/nginx /home/demo/tutorials/basic && docker build -t madt/pyget /home/demo/tutorials/monitoring

cd /home/demo/tutorials/kademlia
sudo docker build -t kademlia .

cd /home/demo/examples 
nano kademlia_iterative.py
(change number of childrens to 30)
python3 kademlia_iterative.py /home/demo/labs/monitoring

cd /app
python3 main.py 80 -q

(or)
hypercorn main:app -b 0.0.0.0:80
```

# navigate to localhost:8990, use demo:demo credentials to login, go to monitoring, press restart