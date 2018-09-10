. env/bin/activate
export FLASK_DEBUG=True
export FLASK_APP=smartNutrition
export SMART_NUTRITION__SETTINGS=config.py
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

sudo service mongod start
flask run --host 0.0.0.0 --port 8000
sudo service mongod stop
