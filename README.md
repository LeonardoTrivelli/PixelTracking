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

## Next Steps

1) Checks on Consistency.
2) Bulk insert from a Contacts scheduled.
3) Add a Grafana Instance to monitor in real time the email openings to maximize A/B testing redemption.
4) Add a Apache Kafka / Apache Pulsar instance to postprocess last insert data (views).

## Prerequisites

Before running this project, ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Environment Variables

Create a `.env` file in the root project directory and set the following environment variables:

```ini
MYSQL_USER=My sql User
MYSQL_PASSWORD=My sql User Password
MYSQL_ROOT_PASSWORD=My sql Root User Password
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=My sql Database name
API_SECRET_KEY=Api Secret key
API_SECRET_ALGORITHM=Secret encryption algo (for example HS256)
API_ACCESS_TOKEN_EXPIRE_MINUTES=30
FERNET_KEY='My Fernet Key for encryption of sensitive data'
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

Once the containers are running, you can access your API service and database as configured.

## Stopping the Services

To stop the running containers, use:

```sh
docker compose down
```

## Debug

If the python_service doesen't start correctly please restart it with docker.

## License

Licence in Api Documentation /docs

---


