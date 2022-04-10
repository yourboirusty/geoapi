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


### Default configuration
`username: root`
`password: 4321tset` but backwards

Some geodata will be available.

## Documentation

### REST API
`localhost:8000/api/swagger` and `localhost:8000/api/redoc`

### WS
Can be tested from a browser using [hoppscotch.io](https://hoppscotch.io/pl/realtime).
#### ws://localhost:8000/ws/geodata?token=<jwt_token>
- final response will be a slug to grab the item from REST API (or `status:"FAILURE"`)
- accepts `{task_id: <task_id>}` as input, returns task status,
- alternatively, `GET geodata/lookup/?task_id=<task_id>`
### Communication diagram
![Address Lookup Diagram](./docs/img/UserAddressLookup.svg)


### Online version
https://rusty-geoapi.herokuapp.com/


### Known issues
- Communication between Celery and Channels is down. Message pushing doesn't work. User has to manually query for status.
- Multiple lookups of same address could be cached to minimize amount of requests to external API.
