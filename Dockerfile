FROM python:3.6

WORKDIR /app

COPY . /app

RUN pip install -U pip \
        && cd /app \
        && pip install -r requirements.txt \
        && python setup.py bdist_wheel \
        && cd dist \
        && pip install flaskr-1.0.0-py3-none-any.whl

EXPOSE 8000
