# Deploy events service

For service description see [README](../../services/events_api/README.md).

## Setting up environment variables

Before running the project, you need to create `.env` files based on the provided `.env.example` templates in `envs` directory of the current folder.

### Step 1: Create .env files

Navigate to the `envs` directory and create the required `.env` files:

    cp .service.env.example .service.env
    cp .common.kafka.env.example .common.kafka.env
    cp .node0.kafka.env.example .node0.kafka.env
    cp .node1.kafka.env.example .node1.kafka.env
    cp .node2.kafka.env.example .node2.kafka.env
    cp .ui.kafka.env.example .ui.kafka.env

### Step 2: Fill in the .env files

Open each `.env` file and update the necessary values.

#### .service.env

    API_HOST=0.0.0.0  # must be equal to API host
    API_PORT=8000  # must be equal to API port
    KAFKA_BOOTSTRAP_SERVERS=kafka-node-0:9092,kafka-node-1:9092,kafka-node-2:9092  # list of servers in the format of container_name:exposed_port
    KAFKA_TOPIC_NAME=test_topic  # name of Kafka topic
    KAFKA_TOPIC_NUM_PARTITIONS=3  # number of partitions for that topic
    KAFKA_TOPIC_REPLICATION_FACTOR=3  # replication factor for that topic


#### .common.kafka.env

    KAFKA_ENABLE_KRAFT=yes  # enable KRaft mode (Kafka without Zookeeper)
    ALLOW_PLAINTEXT_LISTENER=yes  # allow non-encrypted (PLAINTEXT) communication
    KAFKA_CFG_PROCESS_ROLES=broker,controller  # this node acts both as a broker and a controller
    KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER  # listener type used for controller communication
    KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka-node-0:9093,1@kafka-node-1:9093,2@kafka-node-2:9093  # quorum voters with IDs and addresses of all controller nodes
    KAFKA_KRAFT_CLUSTER_ID=abcdefghijklmnopqrstuv  # unique ID for the KRaft cluster
    KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,PLAINTEXT:PLAINTEXT  # map each listener name to its security protocol (all use PLAINTEXT here)

#### .node0.kafka.env

    KAFKA_CFG_NODE_ID=0  # unique node ID used in the KRaft quorum (must match the ID in CONTROLLER_QUORUM_VOTERS)
    KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094  # define where Kafka listens for incoming connections (internal and external)
    KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka-node-0:9092,EXTERNAL://127.0.0.1:9094  # addresses and ports advertised to clients for connection

#### .node1.kafka.env

    KAFKA_CFG_NODE_ID=1  # unique node ID for this broker/controller (must match ID in CONTROLLER_QUORUM_VOTERS)
    KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9095  # listener addresses for internal and external communication
    KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka-node-1:9092,EXTERNAL://127.0.0.1:9095  # advertised addresses for internal Docker network and host machine access

#### .node2.kafka.env

    KAFKA_CFG_NODE_ID=2  # unique node ID for this broker/controller (must match ID in CONTROLLER_QUORUM_VOTERS)
    KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9096  # listener addresses for internal and external communication
    KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka-node-2:9092,EXTERNAL://127.0.0.1:9096  # advertised listener addresses for Docker internal network and host machine access

#### .ui.kafka.env

    KAFKA_CLUSTERS_0_BOOTSTRAP_SERVERS=kafka-node-0:9092,kafka-node-1:9092,kafka-node-2:9092  # list of Kafka broker addresses for cluster connection
    KAFKA_CLUSTERS_0_NAME=kraft  # name assigned to the Kafka cluster
    AUTH_TYPE=LOGIN_FORM  # type of authentication used
    SPRING_SECURITY_USER_NAME=admin  # username for accessing the UI (basic authentication)
    SPRING_SECURITY_USER_PASSWORD=pass  # password for the specified username

## Running

Once the `.env` files are set up, go to the folder `events_api` and run the following command to start all components:

    docker-compose -f docker-compose.local.yml up --build

The API is available now at `localhost:83`. User interface for Kafka is available at `localhost:8081`.
