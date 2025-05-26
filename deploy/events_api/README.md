# Deploy events service

For service description see [README](../../services/events_api/README.md).

## Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `envs` directory of the current folder.

### Step 1: Create .env files

Navigate to the `envs` directory and create the required `.env` files:

    cp .service.env.example .service.env

### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

#### .service.env

    API_HOST=0.0.0.0  # must be equal to API host
    API_PORT=8000  # must be equal to API port


## Running

Once the `.env` files are set up, go to the folder `events_api` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build

The API is available now at `localhost:83`.
