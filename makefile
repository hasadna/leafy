.PHONY: init freeze lint makemigrations serve test bot

bot:
	# venv/bin/python bot.py
	venv/bin/python djang/manage.py bot

init:
	virtualenv venv
	venv/bin/pip install -r requirements.txt

freeze:
	venv/bin/pip freeze > requirements.txt

lint:
	venv/bin/black .

makemigrations:
	venv/bin/python djang/manage.py makemigrations bot
	venv/bin/python djang/manage.py migrate
	venv/bin/python djang/manage.py makemigrations
	# Actually migrate
	venv/bin/python djang/manage.py migrate

serve:
	venv/bin/python djang/manage.py runserver

test:
	venv/bin/python djang/manage.py test txns
