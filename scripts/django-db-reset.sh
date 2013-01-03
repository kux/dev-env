user=$1
pass=$2
database=$3
echo "drop database $database" | mysql -u$user -p$pass -f
echo "create database $database" | mysql -u$user -p$pass -f

django-admin.py syncdb --all --noinput --settings=hostedbento.settings
django-admin.py migrate --fake --settings=hostedbento.settings
django-admin.py createsuperuser --username=root --email=root@root.com --settings=hostedbento.settings


