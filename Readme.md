# git
    git remote add origin https://github.com/username/repository.git
    git push -u origin master
    git rm -r --cached .
    git add .
    git commit -m "updates"
    git push origin master

# pip
    pip install -r requirements.txt

# To check gunicorn processes
    ps ax|grep gunicorn

# To kill all gunicorn processes
    pkill gunicorn



## Gunicorn setup 

# Setting up Gunicorn as a systemd Service
Step 1: Create a systemd Service File
Create a systemd service file for your Gunicorn application:

    sudo nano /etc/systemd/system/lanewatcher.service

# Step 2: Edit the systemd Service File
In the file, enter the following:

    [Unit]
    Description=Gunicorn instance to serve lanewatcher
    After=network.target

    [Service]
    User=root
    Group=www-data
    WorkingDirectory=/var/www/lanewatcher
    Environment="PATH=/var/www/lanewatcher/venv/bin"
    ExecStart=/var/www/lanewatcher/venv/bin/gunicorn lanewatcher.wsgi:application --bind 0.0.0.0:8000 --workers 3

    [Install]
    WantedBy=multi-user.target


Replace yourusername with your actual username. This will be the user that runs the Gunicorn service.
Save and close the file.

# Step 3: Start and Enable the Gunicorn Service
Now you can start the Gunicorn service and enable it to start on boot:

    sudo systemctl start lanewatcher
    sudo systemctl enable lanewatcher

# Step 4: Checking the Status of Your Service
You can check the status of your service at any time with the following command:

    sudo systemctl status lanewatcher

# Managing the Gunicorn Service
To stop the service, you can use the following command:

    sudo systemctl stop lanewatcher

And to restart the service, you can use the following command:

    sudo systemctl restart lanewatcher

With this setup, your Gunicorn service will start automatically when your system boots, and you can easily start, stop, and restart it manually when needed.