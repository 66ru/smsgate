kill `ps ax | awk '/celeryd/{print $1}'`

source /path/to/env/bin/activate
cd /path/to/app/
python manage.py celeryd --settings=settings &
