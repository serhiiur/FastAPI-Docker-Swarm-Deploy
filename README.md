## Introduction
Notes on using Docker


## Notes
-



## Snippets
```bash
# Enter Python 3.13 REPL
docker run --rm -it python:3.13.2-alpine3.21 python

# Enter Node CLI
docker run --rm -it node:22-alpine node

# Run Redis Stack
docker run -d --rm --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# Enter Redis CLI (after running the Redis Stack)
docker exec -it redis-stack redis-cli
```



## Useful Links
- Google Docs:
  - [Push Docker-Image to Dockerhub](https://docs.google.com/document/d/1FwtrfpLbo-aVZZfvS6Onr1De1HZaA0qbvoD6jq7P2dU/edit?tab=t.0#heading=h.w2peqvitph4p)
  - [Push Docker Image to Amazon ECR](https://docs.google.com/document/d/1FwtrfpLbo-aVZZfvS6Onr1De1HZaA0qbvoD6jq7P2dU/edit?tab=t.0#heading=h.24rwh66wzo5y)


