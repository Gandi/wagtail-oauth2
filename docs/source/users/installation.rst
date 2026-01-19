Install and configure wagtail-oauth2
====================================


Installation
------------

`wagtail-oauth2` is available on pypi, you can install with your favorite
packaging tool.

.. note::

   Example using pip

   ::

      pip install wagtail-oauth2

Django's Configuration
----------------------

INSTALLED_APPS
~~~~~~~~~~~~~~

`wagtail-oauth2` is a Django application that must be installed,
so it must be in the `INSTALLED_APPS` list of your settings module.
And, to work, it requires other app that are probably already installed.

Here is the lists of the minimum installed app.

::

   INSTALLED_APPS = [
      # ...
      "django.contrib.auth",
      "django.contrib.contenttypes",
      "django.contrib.sessions",
      "wagtail_oauth2",
      "wagtail.admin",
      "wagtail.users",
      "wagtail.core",
      # ...
   ]


MIDDLEWARE
~~~~~~~~~~

Every authentication system requires a session middleware,
`wagtail-oauth2` does not escape this rule.

::

   MIDDLEWARE = [
      "django.contrib.sessions.middleware.SessionMiddleware"
   ]


TEMPLATES
~~~~~~~~~

`wagtail-oauth2` may render a template `login_error.html` if issues happen
during the OAuth2.0 dance.

The template is provided using django template system in the package,
the settings `APP_DIRS` must be set to `True` in order to render it.

::

   TEMPLATES = [
      {
         "BACKEND": "django.template.backends.django.DjangoTemplates",
         "APP_DIRS": True,
      }
   ]


URLS
~~~~

The oauth2 urls has to be installed before wagtail urls in order to get
them override the defaults ones.

::

   from wagtail_oauth2 import urls as oauth2_urls


   urlpatterns = [
      path("django-admin/", admin.site.urls),
      path("admin/", include(oauth2_urls)),
      path("admin/", include(wagtailadmin_urls)),
      path("documents/", include(wagtaildocs_urls)),
      path("search/", search_views.search, name="search"),
   ]
