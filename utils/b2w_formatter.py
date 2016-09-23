import os
import sys
import json_log_formatter
import socket
from datetime import datetime


class B2WJSONFormatter(json_log_formatter.JSONFormatter):

    def json_record(self, message, extra, record):
        extra['log_message'] = message.replace('"', '\"').replace("\n", " ")
        extra['hostname'] = socket.gethostname()
        extra['application'] = os.getenv("JSONFORMATTER_APP", 'sixpack-ab')
        extra['version'] = os.getenv("JSONFORMATTER_APP_VERSION", '1.00')
        extra['environment'] = os.getenv("JSONFORMATTER_APP_ENV", 'Atlas')
        extra['brand'] = os.getenv("JSONFORMATTER_APP_BRAND", 'B2W')
        extra['log_level'] = record.levelname
        extra['file'] = sys.argv[0]
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
        allowedDateSize = 23
        diff = len(date) - allowedDateSize
        extra['date'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-diff]

        return extra

    def format(self, record):
        message = record.getMessage()
        extra = self.extra_from_record(record)
        json_record = self.json_record(message, extra, record)
        self.mutate_json_record(json_record)
        return "#JSON#"+self.json_lib.dumps(json_record)