# django superuser details
username = admin
email = test@test.com
password = admin

# To check gunicorn processes
ps ax|grep gunicorn

# To kill all gunicorn processes
pkill gunicorn

# to start gunicorn
gunicorn lanewatcher.wsgi:application --bind 0.0.0.0:8000 --workers 3


# git
git remote add origin https://github.com/username/repository.git
git push -u origin master
git rm -r --cached .
git add .
git commit -m "updates"
git push origin master
