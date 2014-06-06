#!/usr/bin/env python
import os
import sys
import logging

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    sentry_errors_log = logging.getLogger("sentry.errors")
    sentry_errors_log.addHandler(logging.StreamHandler())

    from django.core.management import execute_from_command_line
    from raven.contrib.django.raven_compat.models import client

    try:
        execute_from_command_line(sys.argv)
    except Exception, e:
        client.captureException(tags={'doska': 'smsgate'})