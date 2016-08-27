from simple_salesforce import Salesforce
from simple_salesforce import api


class SForceConnector(object):
    def __init__(self, username: str, password: str, sandbox: bool, security_token: str = ''):
        self.session = Salesforce(username=username, password=password, security_token=security_token, sandbox=sandbox)

    def query_raw(self, query):
        results = self.session.query(query)
        return results

    def query(self, query):
        try:
            raw_results = self.query_raw(query)
        except api.SalesforceError as ex:
            raise Exception(ex.content[0]['message'])

        if raw_results['totalSize'] == 0:
            raise Exception('This Query Returns No Results')

        # Remove attributes column in records.
        for record in raw_results['records']:
            record.pop('attributes')

        results = {
            'totalSize': raw_results['totalSize'],
            'size': len(raw_results['records']),
            'done': raw_results['done'],
            'headers': [header for header in raw_results['records'][0].keys()],
            'records': [list(record.values()) for record in raw_results['records']]
        }

        return results

    def insert_into_table(self, table_name, insert_dict):
        response = getattr(self.session, table_name).create(insert_dict)
        return response

    def get_table_fields(self, table_name, fields={}):
        if table_name not in fields:
            fields[table_name] = {field['name'].lower(): field['type']
                                  for field in getattr(self.session, table_name).describe()['fields']
                                  if field['byteLength'] > 0}
        return fields[table_name]

    def get_tables(self, table_names=[]) -> list:
        if len(table_names) == 0:
            table_names.extend(obj['name'] for obj in self.session.describe()['sobjects'] if obj['searchable'])
        return table_names

    def close(self):
        self.session.close()