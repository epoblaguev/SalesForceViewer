import traceback

from models.salesforce_connector import SForceConnector
from views.window_main import MainWindow


class MainController(object):
    def __init__(self, view: MainWindow, model: SForceConnector):
        self.model = model
        self.view = view

        self.view.set_listener_run_query(self._run_query)
        self.view.set_listener_query_more(self._run_query_more)
        self.view.set_listener_table_selected(self._select_table)
        self.view.set_listener_filter_tables(self._filter_tables)

        self.view.tables = self.model.get_tables()

    def show(self):
        self.view.show()

    def _run_query(self):
        self.view.temp_status_text = 'Running Query...'
        try:
            query = self.view.query_text
            results = self.model.query(query)
            self.view.update_results_table(results.headers, results.records)
            self.view.status_text = '{0} / {1} Results'.format(results.size, results.totalSize)
            self.view.query_more_enabled = not results.done
        except Exception as e:
            print(traceback.format_exc())
            self.view.error_message = str(e)

    def _run_query_more(self):
        self.view.temp_status_text = 'Getting More Results...'
        try:
            results = self.model.query_more()
            self.view.update_results_table(results.headers, results.records)
            self.view.status_text = '{0} / {1} Results'.format(results.size, results.totalSize)
            self.view.query_more_enabled = not results.done
        except Exception as e:
            print(traceback.format_exc())
            self.view.error_message = str(e)

    def _select_table(self):
        table_name = self.view.selected_table
        self.view.temp_status_text = 'Generating Query For Table: {0} ...'.format(table_name)
        fields = sorted(self.model.get_table_fields(table_name))
        self.view.query_text = 'SELECT {0} FROM {1}'.format(', '.join(fields), table_name)

    def _filter_tables(self):
        filter_text = self.view.filter_text
        table_names = (name for name in self.model.get_tables() if filter_text.lower() in name.lower())
        self.view.tables = table_names
