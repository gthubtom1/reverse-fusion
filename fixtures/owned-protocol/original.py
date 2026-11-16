"""Owned line protocol: local work continues when the simulated service is unavailable."""
import json
import sys

token = None
expires = 0
items = []
for line in sys.stdin:
    try:
        request = json.loads(line)
        operation = request['op']
        if operation == 'local_sum':
            values = request['values']
            if not isinstance(values, list) or any(type(value) is not int for value in values):
                raise ValueError('bad input')
            response = {'sum': sum(values)}
        elif operation == 'login':
            if not request.get('service_available', True):
                response = {'error': 'service-unavailable'}
            elif request.get('device') != 'owned-device' or request.get('key') != 'owned-test-key':
                response = {'error': 'denied'}
            else:
                token = 'owned-session'
                expires = request['now'] + 30
                response = {'token': token, 'expires': expires}
        elif operation == 'logout':
            token = None
            response = {'closed': True}
        elif operation in ('put', 'list', 'cancel'):
            if token is None or request.get('token') != token:
                response = {'error': 'unauthorized'}
            elif request['now'] >= expires:
                token = None
                response = {'error': 'expired'}
            elif operation == 'put':
                value = request['value']
                if not isinstance(value, str) or not value.strip():
                    raise ValueError('bad input')
                items.append(value.strip())
                response = {'count': len(items)}
            elif operation == 'cancel':
                response = {'cancelled': True}
            else:
                response = {'items': items.copy()}
        else:
            response = {'error': 'unknown-operation'}
    except (ValueError, TypeError, KeyError, AttributeError):
        response = {'error': 'malformed'}
    print(json.dumps(response, sort_keys=True, ensure_ascii=True), flush=True)
