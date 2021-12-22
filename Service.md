# Linux Setup
1. Copy the script to the /usr/bin/ folder  
`sudo cp -r  /usr/bin/*`

1. Create a new service file  
`sudo nano /lib/systemd/system/{your-bot-name}.service`

1. Service file example  
`Review {your-bot-name}.service`  
`Rename {your-bot-name}.service to your bot name`

1. Create a new service user  
`sudo useradd -r -s /bin/false {your-bot-name}_bot_service`  

1. Give the user access to the folders  
`sudo chown -R {your-bot-name}_bot_service /usr/bin/py-scripts && sudo chmod -R u+rwx /usr/bin/py-scripts`

1. Load the new service file  
`sudo systemctl daemon-reload`

1. Enable the service to start on system boot, also start the service using the following commands.  
`sudo systemctl enable {your-bot-name}.service`  
`sudo systemctl start {your-bot-name}.service`

1. Check the status  
`sudo systemctl status {your-bot-name}.service`