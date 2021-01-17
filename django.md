# Django API project + Docker + Travis CI with TDD

## Setup a new project

### 1. Create `Dockerfile` file
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


### 2. Create `docker-compose.yml` file
    version: '3.4'

    services:
    app:
        image: app
        build:
            context: .
        ports:
            - 8000:8000
        volumes:
            - ./app:/app
        command: >
            sh -c "python manage.py wait_for_db &&
                python manage.py migrate &&
                python manage.py runserver 0.0.0.0:8000"
        environment:
            - DB_HOST=db
            - DB_NAME=app
            - DB_USER=postgres
            - DB_PASSWORD=supersecretpassword
        depends_on:
            - db

    db:
        image: postgres:10-alpine
        environment: 
            - POSTGRES_DB=app
            - POSTGRES_USER=postgres
            - POSTGRES_PASSWORD=supersecretpassword



### 3. Create `requirenments.txt` file
    Django>=3.1.3,<3.2.0
    djangorestframework>=3.12.2,<3.13.0
    psycopg2>=2.8.6,<2.9.0
    Pillow>=8.0.1,<8.1.0

    flake8>=3.8.4,<3.9.0

    gunicorn>=20.0.4,<20.1.0


### 4. Create Django project

>- `$ docker-compose run app sh -c "django-admin.py startproject app ."`


### 5. Create `.travis.yml` file
    language: python
    python: 
      - "3.8"

    services:
      - docker

    before_script: pip install docker-compose

    script:
      - docker-compose run app sh -c "python manage.py test && flake8"


### 6. Create `.flake8` file in `./app` folder
    [flake8]
    exclude = 
        migrations
        __pycache__,
        manage.py,
        settings.py


### 7. Create a `core` app and `restframework` in the project
>- `$ docker-compose run app sh -c "python manage.py startapp core"`
>- add `'core'` item in to `settings.py` file into `INSTALLED_APPS` list



    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework.authtoken',
        'core',
    ]

### 8. Create `tests` folder in `./app/core/` folder
> And create `__init__.py` file in `tests` folder.

### 9. Change DB in `settings.py`
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.environ.get('DB_HOST'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
        }
    }

### 10. Add static to `app/urls.py` file
    from django.conf.urls.static import static
    from django.conf import settings

    urlpatterns = [
        ...
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## Important commands

### Start a new project
>`$ docker-compose run --rm app sh -c "django-admin.py startproject app ."`

### Start a new application
>`$ docker-compose run --rm app sh -c "django-admin.py startapp <name>"`

### Run tests
>`$ docker-compose run --rm app sh -c "python manage.py test"`

### Run tests with linter flake8
>`$ docker-compose run --rm app sh -c "python manage.py test && flake8"`

### Create Django super user
>`$ docker-composer run --rm app sh -c "python manage.py createsuperuser"`

### Apply fixtures
>`$ docker-composer run --rm app sh -c "python manage.py loaddata <filename>"`


## Setup Debuger
### 1. Add `docker-compose.debug.yml` file
    version: '3.4'

    services:
    app:
        image: debugapp
        build:
        context: .
        dockerfile: ./Dockerfile
        command: ["sh", "-c", "pip install debugpy -t /tmp && python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678 app/manage.py runserver 0.0.0.0:8000 --nothreading --noreload"]
        ports:
        - 8000:8000
        - 5678:5678

### 2. Make sure that `Dockerfile` contains this row at the end of the file

    CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]

### 3. Make sure that `requirenments.txt` file contains this row

    gunicorn>=20.0.4,<20.1.0

### (Optional) for VSCode only. Add code to vscode workspace file

    ...
	"launch": {
		"version": "0.2.0",
		"configurations": [
			{
				"name": "Docker: Python - Django",
				"type": "docker",
				"request": "launch",
				"preLaunchTask": "docker-run: debug",
				"python": {
					"pathMappings": [
						{
							"localRoot": "${workspaceFolder}/app",
							"remoteRoot": "/app"
						}
					],
					"projectType": "django"
				}
			}
		],
	},
	"tasks": {
		"version": "2.0.0",
		"tasks": [
			{
				"type": "docker-build",
				"label": "docker-build",
				"platform": "python",
				"dockerBuild": {
					"tag": "debugapp:latest",
					"dockerfile": "${workspaceFolder}/Dockerfile",
					"context": "${workspaceFolder}",
					"pull": true
				}
			},
			{
				"type": "docker-run",
				"label": "docker-run: debug",
				"dependsOn": [
					"docker-build"
				],
				"python": {
					"args": [
						"runserver",
						"0.0.0.0:8000",
						"--nothreading",
						"--noreload"
					],
					"file": "manage.py"
				}
			}
		]
	}
    ...


