Here are the instruction to launch a spark cluster with the appropriate python library to execute HOALS

Install google-cloud-sdk : https://cloud.google.com/sdk/ 
Download bdutils : https://github.com/GoogleCloudPlatform/bdutil
execute deploy.sh with your own values


- Go to https://console.cloud.google.com/home/
- Select your billing project
- Go to Cloud Launcher
- look for Hadoop
- Choose number of machines and types (when done, don't forget to delete deployment)
- Go to compute engine 
- Click on master
- Edit
- Enter keys # for me named compute_engine
- Get external ip 
- In local terminal enter : ssh -i compute_engine YOUR EXTERNAL IP
- Then execute deploy.sh (not currently working) 
