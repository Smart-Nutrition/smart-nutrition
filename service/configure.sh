set -e
set -x

echo "Step 0. Install curl,  python3, python-venv"

sudo apt-get -y install curl
sudo apt-get -y install python3
sudo apt-get -y install python3-venv
sudo apt-get -y install sqlite3

echo "Step 0.1 Install node and npm"
curl --silent --location https://deb.nodesource.com/setup_6.x | sudo bash -
sudo apt-get install --yes nodejs

echo "Step 1. Setup pip virutal environment. Add smartNutrition to env."
python3 -m venv env
source env/bin/activate
pip3 install --upgrade pip
pip install -e .

echo "Step 2. Install semantic and dependencies"

echo "# Step 2.2 Install Gulp"
sudo npm install -g gulp

echo "# Step 2.3 Install Semantic UI"
sudo npm install semantic-ui

echo "# Step 3. Install MongoDB"
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org
pip3 install pymongo

echo "# Step 4. Install jshint"
sudo npm install -g jshint
