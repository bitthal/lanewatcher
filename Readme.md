# django superuser details
username = admin
email = test@test.com
password = admin

# To kill all gunicorn processes
pkill gunicorn

# to start gunicorn
gunicorn lanewatcher.wsgi:application --bind 0.0.0.0:8000 --workers 3



