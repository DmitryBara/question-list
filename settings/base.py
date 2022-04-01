import os
from datetime import timedelta


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
	'users.apps.UserConfig',
	'questionnaire.apps.QuestionnaireConfig',

	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django_extensions',
	'graphene_django',
	'import_export',
	'simple_history',
]

GRAPHENE = {
	'SCHEMA': 'server.schema.schema',
	'MIDDLEWARE': [
		'graphql_jwt.middleware.JSONWebTokenMiddleware',    # Provides info.context.user
	],
}

AUTHENTICATION_BACKENDS = [
	'graphql_jwt.backends.JSONWebTokenBackend',
	'django.contrib.auth.backends.ModelBackend',
]

GRAPHQL_JWT = {
	'JWT_VERIFY_EXPIRATION': False,                     # Turned off for easy graphql testing
	'JWT_EXPIRATION_DELTA': timedelta(minutes=5),
	'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}


MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'simple_history.middleware.HistoryRequestMiddleware',
]


ROOT_URLCONF = 'server.urls'


TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]


WSGI_APPLICATION = 'server.wsgi.application'


DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ['DATABASE_NAME'],
		'USER': os.environ['DATABASE_USER'],
		'PASSWORD': os.environ['DATABASE_PASSWORD'],
		'HOST': os.environ['DATABASE_HOST'],
		'PORT': os.environ['DATABASE_PORT'],
		# With ATOMIC_REQUESTS=True we could do validation in any place of request lifecycle (incl. query and mutations)
		'ATOMIC_REQUESTS': True,
	}
}


AUTH_USER_MODEL = 'users.User'


AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
