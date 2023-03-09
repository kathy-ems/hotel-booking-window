#!/bin/sh

source /Users/kathyle/Documents/git/personal/hotel-booking-window/.venv/bin/activate
set -o allexport
source /Users/kathyle/Documents/git/personal/hotel-booking-window/.env
set +o allexport
python3 /Users/kathyle/Documents/git/personal/hotel-booking-window/main.py
