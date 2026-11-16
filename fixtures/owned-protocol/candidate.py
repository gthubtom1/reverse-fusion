"""Independent implementation of the owned finite protocol contract."""
import json
import sys


class Session:
    def __init__(self):
        self.active = False
        self.until = 0
        self.records = []

    def dispatch(self, req):
        op = req['op']
        if op == 'local_sum':
            if not isinstance(req['values'], list) or not all(type(n) is int for n in req['values']):
                return {'error': 'malformed'}
            result = 0
            for n in req['values']:
                result += n
            return {'sum': result}
        if op == 'logout':
            self.active = False
            return {'closed': True}
        if op == 'login':
            if not req.get('service_available', True):
                return {'error': 'service-unavailable'}
            if (req.get('device'), req.get('key')) != ('owned-device', 'owned-test-key'):
                return {'error': 'denied'}
            self.active = True
            self.until = req['now'] + 30
            return {'expires': self.until, 'token': 'owned-session'}
        if op not in ('list', 'put', 'cancel'):
            return {'error': 'unknown-operation'}
        if not self.active or req.get('token') != 'owned-session':
            return {'error': 'unauthorized'}
        if req['now'] >= self.until:
            self.active = False
            return {'error': 'expired'}
        if op == 'list':
            return {'items': list(self.records)}
        if op == 'cancel':
            return {'cancelled': True}
        value = req['value']
        if not isinstance(value, str) or value.strip() == '':
            return {'error': 'malformed'}
        self.records += [value.strip()]
        return {'count': len(self.records)}


session = Session()
for line in sys.stdin:
    try:
        response = session.dispatch(json.loads(line))
    except (ValueError, TypeError, KeyError, AttributeError):
        response = {'error': 'malformed'}
    sys.stdout.write(json.dumps(response, ensure_ascii=True, sort_keys=True) + '\n')
    sys.stdout.flush()
