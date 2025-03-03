# PixelTracking
Application to Track in real time, Marketing campaign email openings

## Description

FastAPi Backend to Track email openings from Marketing Campaigns.
The application use Token for logins to secure routes. An user should be Authenticated to proceede to API calls.
The application need before contacts the digestion of contacts neededs with schedule dates.
For each contact it's possible insert multiple pixels inside the email (for multi-rendering purposes).
The Database Schema:

![Alt text](./assets/image_db_schema.png?raw=true "Schema")

Campaigns is the Master Level
Each Campaigns has one or more Groups

Each scheduled contact is unique for campaign and group.

The application allow to insert multiple pixels inside the same contact. But the pixel number id with pixel uuid must be unique.

The monitoring service is based on the Grafana system hosted on post 9090 served by a Prometheus log storage. There are two levels of monitoring:
- Of Docker instances (containers RAM and usages).
- FastAPI calls (mysql Datasource).

![Alt text](./assets/image_grafana_docker.png?raw=true "Docker")

![Alt text](./assets/image_grafana_pixel.png?raw=true "Pixels")

## Features

- User Authentication
- Create, Read, Update, and Delete Campaigns
- Create, Read, Update, and Delete Groups
- Create, Read, Update, and Delete Contacts
- Create, Read, Update, and Delete Pixels
- Create, Read, Update, and Delete Pixel Openings
- Schedule Contacts
- JWT Token Authentication
- Redis Caching
- Monitoring with Prometheus & Grafana

## Database Schema

![Database Schema](./assets/database_schema.png)

## API Documentation

- [API Documentation](http://localhost:8000/docs)

## API Endpoints

- [API Endpoints](http://localhost:8000/redoc)

## Sample Data

- [Sample Data](./services/python/sample.json)

## Next Steps

1) redis caching to avoid multiple insertions and serve tracking pixel faster.
2) Add a Grafana Instance to monitor in real time the email openings to maximize A/B testing redemption.

## Prerequisites

Before running this project, ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Environment Variables

Create a `.env` file in the root project directory and set the following environment variables:

```ini
MYSQL_USER=xxx
MYSQL_PASSWORD=xxx
MYSQL_ROOT_PASSWORD=xxx
MYSQL_HOST=xxx
MYSQL_PORT=xxx
MYSQL_DATABASE=xxx
API_SECRET_KEY=xxx
API_SECRET_ALGORITHM=xxx
API_ACCESS_TOKEN_EXPIRE_MINUTES=30
FERNET_KEY='xxx='
REDIS_PASSWORD=xxx
REDIS_ROOT_PASSWORD=xxx
```

## Installation & Setup

1. Clone this repository:

   ```sh
   git clone https://github.com/LeonardoTrivelli/OpenFastAI.git
   cd project
   ```

2. Ensure Docker is installed and running.

3. Start the services using Docker Compose:

   ```sh
   docker compose up -d
   ```

## Usage

Once the containers are running, you can access your API service and database as configured. The Database is automatically configured by given sample.json file included in services/python/sample.json .

Some Pixels are already inserted to test fast the API. 
A Redis Caching is set up automatically to save only last 60 minutes refreshes, to overcome Mozzilla Browser automatic refreshes.

The FastAPI framework is used because is very easy to integrate with openapi projects designs

## Stopping the Services

To stop the running containers, use:

```sh
docker compose down
```

## Debug

If the python_service doesen't start correctly please restart it with docker.

## License

Licence in Api Documentation /docs

## Technologies

- [FastAPI](https://fastapi.tiangolo.com/) - API Framework
- [Docker](https://www.docker.com/) - Containerization
- [Redis](https://redis.io/) - Caching
- [MySQL](https://www.mysql.com/) - Database
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data Validation
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Fernet](https://cryptography.io/en/latest/fernet/) - Token Encryption
- [Uvicorn](https://www.uvicorn.org/) - ASGI Server

---


