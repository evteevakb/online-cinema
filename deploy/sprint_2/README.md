# Deploy admin panel for the online cinema

For service description see [service README](../../services/admin/README.md).

## Installation

### Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `envs` directory.

#### Step 1: Create .env files

Navigate to the `envs` directory and create the required `.env` files:

    cp .db.env.example .db.env
    cp .service.env.example .service.env

#### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

##### .db.env

    POSTGRES_DB=test_database  # must be equal to a database name
    POSTGRES_USER=app  # can be modified
    POSTGRES_PASSWORD=test_password  # can be modified
    POSTGRES_HOST=admin-db  # must be equal to a container name
    POSTGRES_PORT=5432  # must be equal to a standard PostgreSQL port

##### .service.env

    ALLOWED_HOSTS=127.0.0.1,localhost,  # can be modified, hosts must be followed with commas
    DEBUG=0  # can be modified, keep 0 (False) for production environment
    SECRET_KEY=test_secret_key  # can be modified
    DJANGO_SUPERUSER_EMAIL=  # can be modified
    DJANGO_SUPERUSER_USERNAME=admin  # can be modified, login for admin panel
    DJANGO_SUPERUSER_PASSWORD=admin  # can be modified, password for admin panel

## Running

Once the `.env` files are set up, go to the folder `sprint_2` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build

The service now is available at `localhost:80`.
