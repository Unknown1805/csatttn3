#!/bin/sh
set -eu

: "${RESTIC_REST_USERNAME:?Missing REST username}"
: "${RESTIC_PASSWORD_FILE:?Missing repository password file}"
test -s "$RESTIC_PASSWORD_FILE"

RESTIC_REST_PASSWORD="$(cat /run/secrets/rest_http_password)"
test -n "$RESTIC_REST_PASSWORD"
export RESTIC_REST_PASSWORD

exec /usr/bin/restic "$@"
