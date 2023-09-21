import os

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', 'you_need_to_set_the_secret_key_in_env')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost, 127.0.0.1').split(', ')

INTERNAL_IPS = ['127.0.0.1']


INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'posts.apps.PostsConfig',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'sorl.thumbnail',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'yatube.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Добавлен контекст-процессор
                'core.context_processors.year.year',
            ],
        },
    },
]

WSGI_APPLICATION = 'yatube.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/auth/login/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'
POSTS_PER_PAGE = 10
TEXT_CROP = 15
TEST_ID = 1
LOGIN_REDIRECT_URL = 'posts:index'

# names
INDEX = 'posts:index'
PROFILE = 'posts:profile'
POST_DETAIL = 'posts:post_detail'
GROUP_LIST = 'posts:group_list'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'
SIGNUP = 'users:signup'
ADD_COMMENT = 'posts:add_comment'
FOLLOW = 'posts:profile_follow'
FOLLOW_INDEX = 'posts:follow_index'
UNFOLLOW = 'posts:profile_unfollow'

# urls
URL_INDEX = '/'
URL_PROFILE = '/profile/Author/'
URL_POST_DETAIL = '/posts/1/'
URL_GROUP_LIST = '/group/test-slug/'
URL_POST_CREATE = '/create/'
URL_POST_EDIT = '/posts/1/edit/'
URL_UNEXSISTING_PAGE = '/unexsisting_page/'
URL_LOGIN_PAGE = '/auth/login/'
URL_ABOUT_AUTHOR = '/about/author/'
URL_ABOUT_TECH = '/about/tech/'
URL_REDIRECT_FROM_CREATE = '/auth/login/?next=/create/'
URL_REDIRECT_FROM_EDIT = '/auth/login/?next=/posts/1/edit/'
URL_REDIRECT_FROM_COMMENT = '/auth/login/?next=/posts/1/comment/'
URL_REDIRECT_FROM_FOLLOW = '/auth/login/?next=/posts/1/follow/'
URL_REDIRECT_FOR_NOT_AUTHOR = '/profile/Not_Author/'
URL_SIGNUP = '/auth/signup/'

# htmls
HTML_INDEX = 'posts/index.html'
HTML_PROFILE = 'posts/profile.html'
HTML_POST_DETAIL = 'posts/post_detail.html'
HTML_GROUP_LIST = 'posts/group_list.html'
HTML_POST_CREATE = 'posts/create_post.html'
HTML_POST_EDIT = 'posts/create_post.html'
HTML_SIGNUP = 'users/signup.html'
HTML_404 = 'core/404.html'
HTML_403 = 'core/403csrf.html'
HTML_FOLLOW = 'posts/follow.html'

# Отправка писем Яндекс-почтой (Не работает на pythonanywhere.com)
RECIPIENT_ADDRESS = os.getenv('RECIPIENT_ADDRESS', 'your_email_on_yandex@yandex.ru')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')
EMAIL_PORT = os.getenv('EMAIL_PORT', '465')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'your_email_on_yandex@yandex.ru')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your_email_on_yandex@yandex.ru')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_strong_email_password')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
