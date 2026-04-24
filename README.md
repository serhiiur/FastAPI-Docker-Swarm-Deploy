## About

Minimal FastAPI application deployed on a Docker Swarm cluster.


## Prerequisites

For demonstration purposes we're going to provision virtual machines using [Lima](https://github.com/lima-vm/lima) to set the Docker Swarm cluster on multiple nodes. You can use any other virtualization tools such as VirtualBox, VMWare etc. The goal of the project is to provide a straightforward way to deploy and maintain a minimal FastAPI application on a Docker Swarm cluster.


## Navigation

- [About](#about)
- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Project Features](#project-features)
- [Project Structure](#project-structure)
- [Docker Swarm Cluster Setup](#docker-swarm-cluster-setup)
- [Deployment](#deployment)
- [Local Development](#local-development)
- [Further Steps](#further-steps)
- [References](#references)


## System Requirements
- Python >=3.12,<3.13
- Docker v1.12+ (for Docker Swarm Mode support)
- (*Optional*) Virtualization Tool such as Lima/VirtualBox/VMWare etc.


## Project Features
- FastAPI + Pydantic
- Alembic for managing database migrations
- JSON logging
- Ruff for linting, Ty for type checking
- Pytest for testing
- Deploy to Docker Swarm multi-node cluster
- Configs and Secrets management using Docker capabilities
- VMs provisioning with Lima
- Integration with Portainer for Docker Swarm cluster monitoring


## Project Structure
```bash
.
├── configs
│   ├── api.env         # Docker Config providing application configuration
├── secrets
│   ├── db_password.txt # Docker Secret to store the database password
├── src
│   ├── alembic         # Configuration for Alembic. Database migrations and files
│   │   ├── ...
│   ├── app
│   │   ├── main.py     # Main FastAPI application entrypoint
│   │   ├── core        # Core application providing shared resources such as settings, schemas, models etc.
│   │   │   ├── ...
│   │   └── users       # Application to manage users on the API level
│   │       ├── ...
│   └── tests           # Project tests
│       ├── ...
├── compose.yml         # Compose file to deploy the application to Docker Swarm cluster
├── logging.config.json # Project logging config providing JSON handler
├── create-vms.sh       # Custom script to provision virtual machine for Docker Swarm deployment
├── Dockerfile          # Project Docker image builder
├── pyproject.toml      # Project configuration and dependencies management
└── uv.lock             # Locked project management file
├── README.md
```


## Docker Swarm Cluster Setup

Basic architecture for our Docker Swarm cluster is

<p>
  <img src="assets/images/infra.png" width=600>
</p>


### Step 1. Provision VMs (nodes) for the Docker Swarm cluster:

**Note**: skip this step if you don't use Lima for provisioning VMs.

```bash
sudo chmod +x ./create-vms.sh
./create-vms.sh manager,worker1,worker2,db,cache
```

### Step 2. Init Docker Swarm cluster:

Initialize Docker Swarm cluster on the Manager node:
```bash
limactl shell manager docker swarm init
```

Copy the join token and address of the Manager node from the output into variables for further steps:
```bash
TOKEN=<docker-swarm-join-token>
MANAGER_ADDR=<manager-node-address>
```

### Step 3. Join nodes to the cluster:

```bash
limactl shell worker1 docker swarm join --token $TOKEN $MANAGER_ADDR
limactl shell worker2 docker swarm join --token $TOKEN $MANAGER_ADDR
limactl shell db      docker swarm join --token $TOKEN $MANAGER_ADDR
limactl shell cache   docker swarm join --token $TOKEN $MANAGER_ADDR
```

List cluster nodes:

```bash
limactl shell manager docker node ls
```

### Step 4. Label nodes (for further deployment):


There are 2 labels:
  - **tag**  - label for tagging nodes to deploy specific services on;
  - **type** - general label used for Portainer to deploy the agent on each node of the stack.


```bash
# connect to the Manager node
limactl shell manager

# label nodes
docker node update --label-add type=fastapi-stack --label-add tag=manager lima-manager
docker node update --label-add type=fastapi-stack --label-add tag=worker  lima-worker1
docker node update --label-add type=fastapi-stack --label-add tag=worker  lima-worker2
docker node update --label-add type=fastapi-stack --label-add tag=db      lima-db
docker node update --label-add type=fastapi-stack --label-add tag=cache   lima-cache
```

Now the application is ready to be deployed on the Docker Swarm cluster.


## Deployment

Deploy the application stack on the Manager node:
```bash
limactl shell manager docker stack deploy -c compose.yml fastapi-stack 
```

Once the stack is deployed, you can verify the services status like this:
```bash
limactl shell manager docker stack services fastapi-stack
# or
limactl shell manager docker stack ps fastapi-stack 
```

If everything's ok, you can ping the API health like this:
```bash
limactl shell manager curl http://127.0.0.1:8000/api/health
```

In order to make the application available on the host machine, you need to create a tunnel for the Manager node:
```bash
limactl tunnel manager
```

The command will output the proxy address (the port is randomly assigned):
```
Set `ALL_PROXY=socks5h://127.0.0.1:<PORT>`, etc.
The instance can be connected from the host as <http://lima-default.internal> via a web browser.
```

Now you can access the application from your host machine like this:
```bash
curl --proxy socks5h://127.0.0.1:<PORT> http://lima-manager.internal:8000/api/health
```

In order to open the application in the browser you have to configure SOCKS5 proxy at 127.0.0.1:<PORT>, then navigate to http://lima-manager.internal:8000/api/health.

The image below shows SOCKS5 proxy configuration for Firefox.

<p>
  <img src="assets/images/firefox_socks5_network_configuration.png" width=400>
</p>

Note that 40333 is the port that was provided by `limactl tunnel` command.  

You can also access the Portainer's UI from the browser of your host machine at [https://lima-manager.internal:9443](https://lima-manager.internal:9443) to monitor your Docker Swarm cluster.



## Local Development

You can run application locally without Docker:

```bash
export PYTHONPATH="src/:$PYTHONPATH"

# generate database migrations
uv run alembic -c src/alembic/alembic.ini revision --autogenerate -m "init commit"

# apply database migrations
uv run alembic -c src/alembic/alembic.ini upgrade head

# run the API
uv run uvicorn src.app.main:app --log-config logging.config.json

# run Ruff, Ty, Pytest
uv run ruff check
uv run ty check
uv run pytest
```


## Further steps

- Add a separate service to provide Admin UI for the FastAPI application.

- Add proxy service such as Nginx or Traefik.

- Add basic CI/CD pipeline using Github Actions.

- Add integration with *Makefile* to manage the project.

- 



## References
- [FastAPI](https://github.com/fastapi/fastapi)
- [Lima](https://github.com/lima-vm/lima)
- [Docker Swarm Mode](https://docs.docker.com/engine/swarm/)
