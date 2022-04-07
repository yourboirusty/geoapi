# GeoApi
The goal of this project is to allow a user to get a physical location based on the IP or a domain.

Main components of the app:
- Django Rest Framework synchronous backend for database access and REST API,
- Celery workers to connect to an external service,
- Async Django Channels backend to notify user about changes to the worker.
## Quickstart

### Requirements

- Docker
- Docker Compose

### Docker instructions
1. `docker-compose --file docker/docker-compose.yaml up --build`


## Documentation

### REST API
`localhost:8000/api/swagger` and `localhost:8000/api/redoc`

### WS
Can be tested from a browser using [hoppscotch.io](https://hoppscotch.io/pl/realtime).
#### ws://localhost:8000/ws/geodata/<str:task-id>
- no auth
- will tell anyone with the ID how's it progressing
- final response will be a slug to grab the item from REST API.

### Communication diagram
![Address Lookup Diagram](./docs/img/UserAddressLookup.svg)
