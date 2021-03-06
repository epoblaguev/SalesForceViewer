import json
import os


def load_config(path=None):
    empty_value = {
        'username': '',
        'password': '',
        'sandbox': False,
        'security_token': ''
    }

    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.sforce_viewer.json')

    if not os.path.exists(path):
        return {'': empty_value}

    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
            data[''] = empty_value
    except Exception as ex:
        print('Exception: {0}'.format(ex))
        data = {'': empty_value}
    finally:
        return data


def save_config(logins: dict, path=None):
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.sforce_viewer.json')
    with open(path, 'w') as json_file:
        json.dump(logins, json_file, indent=4, sort_keys=True)