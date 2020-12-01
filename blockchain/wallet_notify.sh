#!/bin/sh
curl "http://exodus:8000/log/wallet_notify" -d "$@"