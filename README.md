# distributed_consensus
Distributed Consensus Experiment.<br>
<br>
Setup Guide:<br>
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04<br>
<br>
local_settings.py:<br>
Rename local_settings_sample.py to local_settings.py<br>
local_settings.py is used for local development and will be excluded from the repo.<br>
Update the database section of this file with the info from your locally run instance of Postgresdb.<br>
<br>
Update Python installers:<br>
sudo apt-get install python3-distutils<br>
sudo apt-get install python3-apt<br>
<br>
Activate virtual environment and install requirments:<br>
virtualenv --python=python3.9 _distributed_consensus_env<br>
pip install -U -r requirements.txt<br>
<br>
Setup Environment:<br>
sh setup.sh<br>






