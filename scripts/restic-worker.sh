#!/bin/sh
set -eu

: "${RESTIC_REST_USERNAME:?Missing REST username}"
: "${RESTIC_PASSWORD_FILE:?Missing repository password file}"
test -s "$RESTIC_PASSWORD_FILE"
: "${RESTIC_CACERT:?Missing trusted CA certificate}"
test -s "$RESTIC_CACERT"
if [ "${RESTIC_REPOSITORY:-}" != "rest:https://backup-server:8000/csattt/" ]; then
  printf '%s\n' 'STOP: expected the verified HTTPS backup repository.' >&2
  exit 1
fi
for task_argument in "$@"; do
  case "$task_argument" in
    --insecure-tls*|--cacert*|--repo*|-r*|--tls-client-cert*|--option*|-o*|--password-*|--no-lock*)
      printf '%s\n' 'STOP: transport, authentication and lock overrides are not allowed.' >&2
      exit 1 ;;
  esac
done

RESTIC_REST_PASSWORD="$(cat /run/secrets/rest_http_password)"
test -n "$RESTIC_REST_PASSWORD"
export RESTIC_REST_PASSWORD

exec /usr/bin/restic "$@"
