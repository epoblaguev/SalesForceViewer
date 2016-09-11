from abc import ABCMeta, abstractmethod
from collections import namedtuple, OrderedDict

from simple_salesforce import Salesforce
from simple_salesforce import api

Results = namedtuple('Results', 'totalSize size done headers records raw_records')


def _clean_results(raw_results):
    if raw_results['totalSize'] == 0:
        raise Exception('This Query Returns No Results')

    # Remove attributes column in records.
    for record in raw_results['records']:
        record.pop('attributes')

    results = Results(
        totalSize=raw_results['totalSize'],
        size=len(raw_results['records']),
        done=raw_results['done'],
        headers=[header for header in raw_results['records'][0].keys()],
        records=[[_flatten_record_value(val) for val in record.values()] for record in raw_results['records']],
        raw_records=raw_results['records']
    )
    return results


def _flatten_record_value(val):
    if not isinstance(val, OrderedDict):
        return val
    else:
        return ' '.join('[{0}: {1}]'.format(k, _flatten_record_value(val[k])) for k in val.keys() if k != 'attributes')


class AbstractSForceConnector(metaclass=ABCMeta):
    @abstractmethod
    def query_raw(self, query):
        pass

    @abstractmethod
    def query(self, query):
        pass

    @abstractmethod
    def query_more_raw(self):
        pass

    @abstractmethod
    def query_more(self):
        pass

    @abstractmethod
    def insert_into_table(self, table_name, insert_dict):
        pass

    @abstractmethod
    def get_table_fields(self, table_name, fields={}):
        pass

    @abstractmethod
    def get_tables(self, table_names=[]) -> list:
        pass

    @abstractmethod
    def close(self):
        pass


class SForceConnector(AbstractSForceConnector):
    def __init__(self, username: str, password: str, sandbox: bool, security_token: str = '', _sf_lib=Salesforce):
        self.session = _sf_lib(username=username, password=password, security_token=security_token, sandbox=sandbox)
        self.next_record_url = None
        self.prev_results = None
        self.prev_size = None
        self.loaded_tables = []
        self.loaded_fields = {}

    def query_raw(self, query):
        results = self.session.query(query)
        self.next_record_url = None if results['done'] else results['nextRecordsUrl']
        return results

    def query(self, query):
        try:
            raw_results = self.query_raw(query)
        except api.SalesforceError as ex:
            raise Exception(ex.content[0]['message'])
        results = _clean_results(raw_results)
        self.prev_results = results.records
        self.prev_size = results.size
        return results

    def query_more_raw(self):
        if self.next_record_url is None:
            raise Exception('You must run a query first.')
        results = self.session.query_more(self.next_record_url, True)
        self.next_record_url = None if results['done'] else results['nextRecordsUrl']
        return results

    def query_more(self):
        try:
            raw_results = self.query_more_raw()
        except api.SalesforceError as ex:
            raise Exception(ex.content[0]['message'])
        results = _clean_results(raw_results)
        self.prev_results.extend(results.records)
        self.prev_size += results.size
        return results._replace(records=self.prev_results, size=self.prev_size)

    def insert_into_table(self, table_name, insert_dict):
        response = getattr(self.session, table_name).create(insert_dict)
        return response

    def get_table_fields(self, table_name, reload=False):
        if table_name not in self.loaded_fields or reload:
            self.loaded_fields[table_name] = {field['name']: field
                                              for field in getattr(self.session, table_name).describe()['fields']}
        return self.loaded_fields[table_name]

    def get_tables(self, reload=False) -> list:
        if len(self.loaded_tables) == 0 or reload:
            self.loaded_tables = [obj['name'] for obj in self.session.describe()['sobjects'] if obj['searchable']]
        return self.loaded_tables

    def close(self):
        self.session.close()