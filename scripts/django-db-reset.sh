user=$1
pass=$2
database=$3
settings_mod=$4
port=$5
socket=$6
port_statement=""
socket_statement=""
if [ -n "$port" ]; then
   port_statement="--port=$port"
fi

if [ -n "$socket" ]; then
   socket_statement="--socket=$socket"
fi

echo $port_statement
echo $socket_statement

echo "drop database $database" | mysql -u$user -p$pass -f $port_statement $socket_statement
echo "create database $database" | mysql -u$user -p$pass -f $port_statement $socket_statement

django-admin.py syncdb --all --noinput --settings=$settings_mod
django-admin.py migrate --fake --settings=$settings_mod
django-admin.py createsuperuser --username=root --email=root@root.com --settings=$settings_mod


echo "update django_site set domain='localhost:8000', name='localhost' where id=1;" | mysql -u$user -p$pass -f $port_statement $socket_statement $database

echo "insert into django_template(id, name, content) values(1, 'simple.html', '{% load cms_tags sekizai_tags menu_tags %}\n<html>\n<head>\n{% render_block "'"'"css"'"'" %}\n</head>\n<body>\n{% cms_toolbar %}\n{% show_menu %}\n{% placeholder content %}\n{% render_block "'"'"js"'"'" %}\n</body>\n</html>');" | mysql -u$user -p$pass -f $port_statement $socket_statement $database

echo "insert into django_template_sites(id, template_id, site_id)values(1, 1, 1);" | mysql -u$user -p$pass -f $port_statement $socket_statement $database

