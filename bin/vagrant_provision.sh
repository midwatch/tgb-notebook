export DEBIAN_FRONTEND=noninteractive

echo "Set Time Zone"
timedatectl set-timezone America/Los_Angeles

echo "Adding third party PPAs"
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

echo "Add Ubuntu Dependencies"
apt-get update
apt-get upgrade -y
xargs apt-get install -y < /vagrant/project.d/requirements-dev.txt

echo "Installing python dependencies"
/usr/bin/python3 -m pip install --upgrade -r /vagrant/project.d/requirements-py3.txt
