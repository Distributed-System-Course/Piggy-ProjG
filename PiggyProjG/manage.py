#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import py_eureka_client.eureka_client as eureka_client

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projg.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


eureka_server = "http://10.151.102.74:8761/"

if __name__ == '__main__':
    eureka_client.init(
        eureka_server="http://10.151.102.74:8761/",
        app_name="User",
        instance_host='10.151.102.74',
        instance_port=9000,
    )
    main()
