#!/usr/bin/env bash
# Start or update the demo index on the testbed. Run as root from this folder
# in the checkout on the server:  sudo ./deploy.sh
#
# It does not touch the Caddy front proxy. The public route is a separate
# step, after the default passwords are replaced (README.md).
set -euo pipefail
cd "$(dirname "$0")"

docker network inspect pid-relay_default > /dev/null 2>&1 || {
    echo "Network pid-relay_default not found. Is the pid-relay stack up?" >&2
    exit 1
}

if [ ! -f .env ]; then
    umask 077
    sed "s|^FDP_JWT_SECRET_KEY=.*|FDP_JWT_SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n')|" \
        .env.example > .env
    echo "Wrote .env with a new JWT secret."
fi

docker compose pull --quiet
docker compose up -d --wait
docker compose ps
./secure-defaults.sh
