#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    # os.environ.setdefault("FACEBOOK_API", "1550163905299791|cQifs91ZQE2hBdNExR8S3iEliGI")
    # os.environ.setdefault("BOT_API", "175543200:AAHPf9hWdtuRQ2TDT9ih_jtUrtuBYblyV1k")
    # os.environ.setdefault("FACEBOOK_ID", "1544715355785805")
    # os.environ.setdefault("TG_CHANNEL_ID", "@channnil")
    # os.environ.setdefault("LAST_POST_ID", "1668439916746681")
    os.environ.setdefault("FACEBOOK_API", "985100678236866|iK2OTbm3ZzvGITYXeTgQGOHJaDM")
    os.environ.setdefault("BOT_API", "175543200:AAHPf9hWdtuRQ2TDT9ih_jtUrtuBYblyV1k")
    os.environ.setdefault("FACEBOOK_ID", "1026639197392218")
    os.environ.setdefault("TG_CHANNEL_ID", "@channnil")
    os.environ.setdefault("LAST_POST_ID", "1032002826855855")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
