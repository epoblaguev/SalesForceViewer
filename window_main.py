import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from salesforce_connector import SForceConnector
from custom_widgets import SOQLHighlighter, ResultsTable


class MainWindow(QWidget):
    def __init__(self, sforce_connection: SForceConnector):
        super().__init__()

        # Salesforce
        self.sf_con = sforce_connection

        # Popups
        self.error_message = QMessageBox()
        self.error_message.setIcon(QMessageBox.Warning)

        # INIT ELEMENTS
        self.root = QHBoxLayout(self)
        self.btn_refresh = QPushButton('Run Query')
        self.frame_nw = QFrame()
        self.layout_nw = QVBoxLayout()
        self.textbox_ne = QTextEdit()
        self.table_s = ResultsTable()
        self.splitter_h = QSplitter(Qt.Horizontal)
        self.splitter_v = QSplitter(Qt.Vertical)
        self.table_list = QListWidget()
        self.table_searchbox = QLineEdit()
        self.syntax_highlighter = SOQLHighlighter(self.textbox_ne)

        # --- ARRANGE ELEMENTS ---

        # Top Left
        self.frame_nw.setFrameShape(QFrame.StyledPanel)
        self.frame_nw.setLayout(self.layout_nw)
        self.layout_nw.addWidget(self.btn_refresh)
        self.layout_nw.addWidget(self.table_searchbox)
        self.layout_nw.addWidget(self.table_list)
        self.btn_refresh.clicked.connect(self.run_query)
        self.table_list.doubleClicked.connect(self.select_table)
        self.table_searchbox.textChanged.connect(self.filter_tables)

        # Top Right
        self.textbox_ne.setFrameShape(QFrame.StyledPanel)

        # Bottom
        self.table_s.setFrameShape(QFrame.StyledPanel)

        # Splitters
        self.splitter_h.addWidget(self.frame_nw)
        self.splitter_h.addWidget(self.textbox_ne)
        self.splitter_v.addWidget(self.splitter_h)
        self.splitter_v.addWidget(self.table_s)

        # Root
        self.root.addWidget(self.splitter_v)

        # Populate Sforce Stuff
        for table_name in self.sf_con.get_tables():
            self.table_list.addItem(QListWidgetItem(table_name))

        # Finalize
        self.setWindowTitle('SalesForce Viewer')
        self.show()

    def run_query(self):
        try:
            query = self.textbox_ne.toPlainText()
            results = self.sf_con.query(query)
            self.table_s.set_data(results['headers'], results['records'])
        except Exception as e:
            self.error_message.setText(str(e))
            self.error_message.show()

    def clear_table(self):
        self.table_s.clear_data()

    def select_table(self):
        table_name = self.table_list.currentItem().text()
        fields = self.sf_con.get_table_fields(table_name)
        self.textbox_ne.setText('SELECT {0} FROM {1}'.format(', '.join(fields), table_name))

    def filter_tables(self):
        filter = self.table_searchbox.text()
        table_names = (name for name in self.sf_con.get_tables() if filter.lower() in name.lower())
        while self.table_list.count() > 0:
            self.table_list.takeItem(0)

        for name in table_names:
            self.table_list.addItem(QListWidgetItem(name))
