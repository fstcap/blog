FROM python:3.6

WORKDIR /app

COPY product/config.py /usr/local/var/flaskr-instance/config.py

COPY dist/flaskr-1.0.0-py3-none-any.whl /app/flaskr-1.0.0-py3-none-any.whl

RUN cd /app \
        && pip install flaskr-1.0.0-py3-none-any.whl \
        && export FLASK_APP=flaskr \
        && flask init-db \
        && pip install gunicorn

EXPOSE 8000

CMD gunicorn -w 4 -b 0.0.0.0:8000 "flaskr:create_app()"
