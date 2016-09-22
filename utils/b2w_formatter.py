import json_log_formatter
import socket
import threading
import sys
from datetime import datetime


class B2WJSONFormatter(json_log_formatter.JSONFormatter):

    def json_record(self, message, extra, record):
        import ipdb;ipdb.set_trace()

        extra['log_message'] = message.replace('"', '\"').replace("\n", " ")
        extra['hostname'] = socket.gethostname()
        extra['application'] = 'dynamic-pricing'
        extra['version'] = '1.00'
        extra['environment'] = 'atlas'
        extra['brand'] = 'b2w'
        extra['customer_id'] = '000000'
        extra['order_id'] = '000000'
        extra['tid'] = '000000'
        if 'log_level' not in extra:
            extra['log_level'] = 'WARNING'
        extra['thread_name'] = threading.current_thread().name
        extra['class'] = 'default'
        extra['file'] = sys.argv[0]
        extra['method'] = 'followCompetitorsPricing'
        extra['throwable'] = {}
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
        allowedDateSize = 23
        diff = len(date) - allowedDateSize
        extra['date'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-diff]
        return extra

    def format(self, record):
        import ipdb;
        ipdb.set_trace()

        message = record.getMessage()
        extra = self.extra_from_record(record)
        json_record = self.json_record(message, extra, record)
        self.mutate_json_record(json_record)
        return "#JSON#"+self.json_lib.dumps(json_record)