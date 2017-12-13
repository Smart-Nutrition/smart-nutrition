rm var/db.sqlite3
mkdir var
sqlite3 var/db.sqlite3 < smartNutrition/static/sql/createdb.sql
echo "DB Created Successfully"
