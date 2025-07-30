# django-zakka - Assorted Django helpers

**django-zakka** is a collection of assorted mini apps and helpers to be reused in various Django projects

# Django Apps

## zakka.contrib.celery

Small celery view and custom command to help with viewing and running arbitrary tasks

## zakka.contrib.utils

Small app to collect assorted, useful [template tags and filters].

# Other Tools

## zakka.http

Wraps [requests] library with some tools to make it easier to assign a User-Agent to all requests.

## zakka.mixins.command

Helpers for writing [django-admin commands].

## zakka.permissions

Useful permissions Mixins

## zakka.test:TestCase

TestCase base class to make it easier to load other test data

[django-admin commands]: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands
[requests]: https://github.com/psf/requests
[template tags and filters]: https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
