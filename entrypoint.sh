#!/bin/sh
set -e

python proxy.py \
  --listen-port "$LISTEN_PORT" \
  --smtp-host "$SMTP_HOST" \
  --smtp-port "$SMTP_PORT" \
  --smtp-user "$SMTP_USER" \
  --smtp-pass "$SMTP_PASS" \
  --ssl-outbound