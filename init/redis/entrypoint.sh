#!/bin/bash

if [[ -z "$REDIS_USER_NAME" || -z "$REDIS_USER_PASSWORD" || -z "$REDIS_PASSWORD" ]]; then
  echo "Error: variables REDIS_USER_NAME, REDIS_USER_PASSWORD or REDIS_PASSWORD not set"
  exit 1
fi

cat <<EOF > /data/users.acl
user $REDIS_USER_NAME on >$REDIS_USER_PASSWORD ~* +@all
EOF

exec redis-server --requirepass "$REDIS_PASSWORD" --aclfile /data/users.acl