import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%6no6+8!lu43k$zf(oso&28z8z=@8em=tcn8s-c%d)f_=k%#xb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# helyi
ALLOWED_HOSTS = ['127.0.0.1']
########################################### innovatív.hu
# ALLOWED_HOSTS = ['dev.innovativnapelem.hu']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'innovativ',

    'tinymce',

    # 'channels',

    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    ########################################### innovatív.hu
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    # A staikus fájlok összegyűjtéséhez: python manage.py collectstatic

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django_otp.middleware.OTPMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inka.urls'

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

                # position változót ad hozzá a sablonok contextéhez:
                'innovativ.context_processors.menu_context',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'inka.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # helyi
        'NAME': 'inka',
        'USER': 'root',
        'PASSWORD': 'gg580219',
        ########################################### innovatív.hu
        # 'NAME': 'cdjyocle_inka',
        # 'USER': 'cdjyocle',
        # 'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 3306
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'hu-HU'
USE_L10N = True  # Engedélyezze a helyi formázást
USE_THOUSAND_SEPARATOR = True  # Engedélyezze az ezres tagolást

TIME_ZONE = 'Europe/Budapest'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static',]
########################################### innovatív.hu
# STORAGES = {
#     "default": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TINYMCE_DEFAULT_CONFIG = {
    'selector': 'textarea',
    # 'resize': 'both',
    'plugins': "link image table pagebreak emoticons preview lists",
    'toolbar': 'undo redo | formatselect | bold italic | alignleft aligncenter alignright'
               ' | bullist numlist outdent indent | link image',
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # SMTP szerver címe
EMAIL_PORT = 587  # SMTP port
EMAIL_USE_TLS = True  # TLS használata
EMAIL_HOST_USER = 'bojtor.gabor@gmail.com'  # Az SMTP felhasználóneve
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_PASSWORD")  # Az SMTP jelszava
DEFAULT_FROM_EMAIL = 'bojtor.gabor@gmail.com'  # Az alapértelmezett feladó e-mail címe


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'cdjyocle.loginssl.com'  # SMTP szerver címe
# EMAIL_PORT = 465  # SMTP port
# EMAIL_USE_TLS = True  # TLS használata
# EMAIL_HOST_USER = '_mainaccount@flyover.corex.bg'  # Az SMTP felhasználóneve
# EMAIL_HOST_PASSWORD = os.getenv("DJANGO_PASSWORD")  # Az SMTP jelszava
# EMAIL_HOST_PASSWORD = 'Rcb(oQ292LM)7b'  # Az SMTP jelszava
# DEFAULT_FROM_EMAIL = 'ugyfelszolgalat@innovativnapelem.hu'  # Az alapértelmezett feladó e-mail címe