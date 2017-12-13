set -e
set -x

sudo apt-get install python3-dev
sudo apt-get install python3-venv

python3 -m venv env
source env/bin/activate
pip3 install --upgrade pip
pip3 install -e .
