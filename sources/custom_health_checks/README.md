# Custom health checks

## Table of Contents
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Requirements](#requirements)
- [What it does](#what-it-does)
- [Installation](#installation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Requirements

- [django-health-check](https://pypi.org/project/django-health-check/)

## What it does

In [backends.py](backends.py) there are custom health checks for backend, like database health check, that checks whether the connection to the database is OK.

## Installation

1. Install the requirements

   ```python
   INSTALLED_APPS = [
       'health_check', # requirement
       "custom_health_checks", # this app
   ]
   ```

2. Register the custom health check to the `health_check` from [apps.py](apps.py)

   ```python
   class CustomHealthChecksAppConfig(AppConfig):
   name = 'custom_health_checks'

   def ready(self):
       from .backends import DatabaseHealthCheck
       plugin_dir.register(DatabaseHealthCheck)
   ```

3. Map the `health_check.urls` in the project's `urls.py`.

   If you want to have the default `health_check` view, map it like this:

   ```python
   urlpatterns = [
       # ...
       path("healthz/", include('health_check.urls'))
   ]
   ```

   If you want to have a custom, e.g. a JSON only view, map it like this:

   ```python
   import views
   urlpatterns = [
       # ...
       path(r'healthz', views.HealthCheckCustomView.as_view(), name='healthz'),
   ]
   ```
