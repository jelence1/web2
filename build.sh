#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py flush --no-input

python manage.py collectstatic --no-input

python manage.py loaddata data.json
python manage.py makemigrations
python manage.py migrate