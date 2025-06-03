# Events service

The `events` api service is responsible for handling requests which produces messages to kafka.

## Endpoints

- **GET** `/api/health`  
  Returns service health status.

- **POST** `/api/v1/events/filter`
  Accepts a JSON payload:
  ```json
  {
    "user_id": "<string>",
    "film_id": "<string>",
    "filter_by": "<string>",
  }
  ```
  Produces movie search filter usage event to Kafka. 

- **POST** `/api/v1/events/video_quality`  
  Accepts a JSON payload:
  ```json
  {
    "user_id": "<string>",
    "film_id": "<string>",
    "before_quality": "<string>",
    "after_quality": "<string>"
  }
  ```
  Produces a video quality change event to Kafka.

- **POST** `api/v1/events/video_stop`  
  Accepts a JSON payload:
  ```json
  {
    "user_id": "<string>",
    "film_id": "<string>",
    "stop_time": "<string>",
  }
  ```
  Produces a video stop event to Kafka.

## Installation

For installation see [deploy documentation](../../deploy/events_api/README.md).

## Testing

For testing you can use [postman collection](./tests/postman_tests.json).

## Contributors

- [@Escros1](https://github.com/Escros1)
- [@evteevakb](https://github.com/evteevakb)
- [@IstyxI](https://github.com/IstyxI)
- [@wegas66](https://github.com/wegas66)
