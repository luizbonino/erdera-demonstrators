#!/usr/bin/env bash
# Replace the passwords of the FDP's two default accounts with random ones,
# before the index gets a public route. Talks to the FDP on 127.0.0.1:8083,
# which compose.yml publishes on the server only.
#
# The new passwords go to ./admin-credentials (mode 600) and are not printed.
# Safe to run again: if the default admin password no longer works, it stops.
set -euo pipefail
cd "$(dirname "$0")"

FDP=http://127.0.0.1:8083
OUT=admin-credentials

for i in $(seq 1 60); do
    curl -sf -o /dev/null "$FDP" && break
    sleep 3
done
curl -sf -o /dev/null "$FDP" || { echo "The FDP does not answer on $FDP." >&2; exit 1; }

# POST /tokens answers 200 with {"token": ...}, or 401 with a Turtle body.
default_login() {
    curl -s -o "$1" -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
        -d '{"email": "albert.einstein@example.com", "password": "password"}' \
        "$FDP/tokens"
}

body=$(mktemp)
trap 'rm -f "$body"' EXIT
status=$(default_login "$body")
if [ "$status" = 401 ]; then
    echo "The default admin password is already changed. Nothing to do."
    exit 0
fi
[ "$status" = 200 ] || { echo "Unexpected answer $status from $FDP/tokens." >&2; exit 1; }
token=$(jq -r .token "$body")

umask 077
: > "$OUT.new"
users=$(curl -sf -H "Authorization: Bearer $token" "$FDP/users")
for email in nikola.tesla@example.com albert.einstein@example.com; do
    uuid=$(jq -r --arg e "$email" '.[] | select(.email == $e) | .uuid' <<<"$users")
    [ -n "$uuid" ] || { echo "No account $email, skipped."; continue; }
    password=$(openssl rand -base64 24)
    curl -sf -o /dev/null -X PUT -H "Authorization: Bearer $token" \
        -H 'Content-Type: application/json' \
        -d "$(jq -n --arg p "$password" '{password: $p}')" \
        "$FDP/users/$uuid/password"
    printf '%s\t%s\n' "$email" "$password" >> "$OUT.new"
    echo "Changed the password of $email."
done
mv "$OUT.new" "$OUT"

# Check that the old admin password is refused now.
status=$(default_login /dev/null)
if [ "$status" != 401 ]; then
    echo "The default admin password is not refused (HTTP $status). Do not open the route." >&2
    exit 1
fi
echo "Default passwords replaced. Credentials are in $(pwd)/$OUT (mode 600)."
