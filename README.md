Deploy on ec2

I use the service approach because the ec2 instance is quite small and docker can be heavy for it.
It was hard because I had to create a service that run the fastapi app instead of just running the app.
Because if I just run the app, the app will be attached to the terminal and if the terminal is closed the app will be closed too.

This was fun, but definitely not the best way to deploy a fastapi app.