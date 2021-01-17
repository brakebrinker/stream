FROM python:3.8.6-alpine

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
ADD requirements.txt .
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN python -m pip install -r requirements.txt
RUN apk del .tmp-build-deps

WORKDIR /app
ADD ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user && chown -R user:user /vol/ && chmod -R 755 /vol/web
USER user

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]