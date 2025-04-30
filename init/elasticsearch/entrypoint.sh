#!/bin/sh

if [[ -z "$ELASTIC_HOST" || -z "$ELASTIC_PORT" || -z "$ELASTIC_USER" || -z "$ELASTIC_PASSWORD" ]]; then
  echo "Error: variables ELASTIC_HOST, ELASTIC_PORT, ELASTIC_USER and/or ELASTIC_PASSWORD not set"
  exit 1
fi


BASE_URL="http://${ELASTIC_HOST}:${ELASTIC_PORT}"


for index in movies genres persons; do
  response=$(curl -s -X PUT "${BASE_URL}/${index}" \
                  -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
                  -H "Content-Type: application/json" \
                  -d "@/init/${index}_schema.json")

  if echo "$response" | grep -q '"acknowledged":true'; then
    echo "SUCCESS: Index ${index} successfully created"
  elif echo "$response" | grep -q '"type":"resource_already_exists_exception"'; then
    echo "WARNING: Index ${index} already exists"
  else
    echo "ERROR: Failed to create index ${index}: $response"
    exit 1
  fi
done 

response=$(curl -s -X POST "${BASE_URL}/_bulk" \
                -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
                -H "Content-Type: application/json" \
                --data-binary "@/init/dump.json")

if echo "$response" | grep -q '"errors":false'; then
  echo "SUCCESS: Data successfully added to indexes"
else
  echo "ERROR: Failed to add data: $response"
  exit 1
fi

exit 0
