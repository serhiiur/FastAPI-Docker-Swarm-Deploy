## About

Minimal FastAPI application deployed on a multi-nodes Docker Swarm cluster.


## Navigation

- [About](#about)
- [System Requirements](#system-requirements)
- [Project Features](#project-features)
- [Project Structure](#project-structure)
- [Swarm Cluster Setup](#swarm-cluster-setup)
- [Deployment](#deployment)
- [Local Development Snippets](#local-development-snippets)
- [Further Steps](#further-steps)


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
- Deployment to Docker Swarm cluster with multiple nodes
- Configs and Secrets management using Docker capabilities
- VMs provisioning with Lima
- Basic CI/CD pipeline using Github Actions


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


## Swarm Cluster Setup

Basic architecture for our Docker Swarm cluster is
![Infrastructure](assets/images/infra.png)

For provisioning cluster nodes, we use [Lima](https://github.com/lima-vm/lima), but you can use any other tool such as VirtualBox, VMWare etc.


### Step 1. Provision VMs (nodes) for the Docker Swarm cluster:

**Note**: skip this step if you don't use [Lima](https://github.com/lima-vm/lima).

```bash
sudo chmod +x ./create-vms.sh
./create-vms.sh manager,worker1,worker2,db,cache
```

### Step 2. Init Docker Swarm cluster:

```bash
# connect to the Manager node and initialize the Docker Swarm cluster
limactl shell manager
docker swarm init
```

Copy the join token and address of the Manager node from the output into variables for further steps:
```bash
TOKEN=<docker-token>
MANAGER_ADDR=<manager-node-address>
```

### Step 3. Join other nodes to the cluster:

```bash
# connect to the Worker1 node and join the cluster
limactl shell worker1
docker swarm join --token $TOKEN $MANAGER_ADDR

# connect to the Worker2 node and join the cluster
limactl shell worker2
docker swarm join --token $TOKEN $MANAGER_ADDR

# connect to the Database node and join the cluster
limactl shell db
db docker swarm join --token $TOKEN $MANAGER_ADDR

# connect to the Cache node and join the cluster
limactl shell cache
docker swarm join --token $TOKEN $MANAGER_ADDR
```

Verify cluster nodes:

```bash
# connect to the Manager node and list nodes of the cluster
limactl shell manager
docker node ls
```

### Step 4. Tag nodes (for further deployment):

The list of tags is:
  - manager
  - worker
  - db
  - cache

```bash
# connect to the Manager node
limactl shell manager

# tag nodes
docker node update --label-add TAG=manager lima-manager
docker node update --label-add TAG=worker lima-worker1
docker node update --label-add TAG=worker lima-worker2
docker node update --label-add TAG=db lima-db
docker node update --label-add TAG=cache lima-cache
```

Now the application is ready to be deployed on the Docker Swarm cluster.



## Deployment

To deploy the stack use the following command:
```bash
docker stack deploy -c compose.yml fastapi-stack 
```

Once the stack is deployed, open [http://localhost:8000/api/schema/docs](http://localhost:8000/api/schema/docs) in your browser
and make sure the application in accessible.

Additionally you can use the commands below to inspect the cluster:
```bash

```










## Local Development Snippets

You can run application locally without Docker. It's useful during development:

```bash
 export PYTHONPATH="src/:$PYTHONPATH"

# generate database migrations
uv run alembic -c src/alembic/alembic.ini revision --autogenerate -m "init commit"

# apply database migrations
uv run alembic -c src/alembic/alembic.ini upgrade head

# run the application
uv run uvicorn src.app.main:app --log-config logging.config.json\

# run Ruff, Ty, Pytest
uv run ruff check
uv run ty check
uv run pytest
```


## Further steps

- Add Admin UI for the FastAPI application

- Add proxy service such as Nginx or Traefik

- 