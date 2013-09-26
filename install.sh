virtualenv --no-site-packages --distribute .
source bin/activate
pip install -r requirements.txt
mkdir db
mkdir logs
mkdir htdocs
mkdir htdocs/static
python manage.py collectstatic --noinput
