from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from salesforce_connector import SForceConnector
from custom_widgets import SOQLHighlighter, ResultsTable


class MainWindow(QMainWindow):
    def __init__(self, sforce_connection: SForceConnector, parent=None):
        super(MainWindow, self).__init__(parent)

        # Salesforce
        self.sf_con = sforce_connection

        # Popups
        self.error_message = QMessageBox()
        self.error_message.setIcon(QMessageBox.Warning)

        # INIT ELEMENTS
        self.root_frame = QFrame()
        self.root_layout = QHBoxLayout()
        self.btn_query = QPushButton('Run Query')
        self.btn_query_more = QPushButton('Query More')
        self.frame_nw = QFrame()
        self.frame_ne = QFrame()
        self.layout_nw = QVBoxLayout()
        self.layout_ne = QVBoxLayout()
        self.txt_query = QTextEdit()
        self.table_s = ResultsTable()
        self.splitter_h = QSplitter(Qt.Horizontal)
        self.splitter_v = QSplitter(Qt.Vertical)
        self.table_list = QListWidget()
        self.table_searchbox = QLineEdit()
        self.syntax_highlighter = SOQLHighlighter(self.txt_query)
        self.status_bar = QStatusBar()

        # --- ARRANGE ELEMENTS ---

        # Top Left
        self.frame_nw.setFrameShape(QFrame.StyledPanel)
        self.frame_nw.setLayout(self.layout_nw)
        self.layout_nw.addWidget(self.table_searchbox)
        self.layout_nw.addWidget(self.table_list)
        self.table_searchbox.setPlaceholderText('Filter Tables')

        # Top Right
        self.frame_ne.setFrameShape(QFrame.StyledPanel)
        self.frame_ne.setLayout(self.layout_ne)
        self.layout_ne.addWidget(self.txt_query)
        self.layout_ne.addWidget(self.btn_query)
        self.layout_ne.addWidget(self.btn_query_more)
        self.txt_query.setFrameShape(QFrame.StyledPanel)
        self.btn_query_more.setDisabled(True)

        # Bottom
        self.table_s.setFrameShape(QFrame.StyledPanel)
        self.setStatusBar(self.status_bar)

        # Splitters
        self.splitter_h.addWidget(self.frame_nw)
        self.splitter_h.addWidget(self.frame_ne)
        self.splitter_v.addWidget(self.splitter_h)
        self.splitter_v.addWidget(self.table_s)

        # Root
        self.setCentralWidget(self.root_frame)
        self.root_layout.addWidget(self.splitter_v)
        self.root_frame.setLayout(self.root_layout)

        # Actions
        self.btn_query.clicked.connect(self.run_query)
        self.btn_query_more.clicked.connect(self.run_query_more)
        self.table_list.doubleClicked.connect(self.select_table)
        self.table_searchbox.textChanged.connect(self.filter_tables)

        # Populate Sforce Stuff
        for table_name in self.sf_con.get_tables():
            self.table_list.addItem(QListWidgetItem(table_name))

        # Finalize
        self.setWindowTitle('SalesForce Viewer')

    def run_query(self):
        try:
            query = self.txt_query.toPlainText()
            results = self.sf_con.query(query)
            self.table_s.set_data(results.headers, results.records)
            self.status_bar.showMessage('{0} / {1} Results'.format(results.size, results.totalSize))
            self.btn_query_more.setDisabled(results.done)
        except Exception as e:
            self.error_message.setText(str(e))
            self.error_message.show()

    def run_query_more(self):
        try:
            results = self.sf_con.query_more()
            self.table_s.set_data(results.headers, results.records)
            self.status_bar.showMessage('{0} / {1} Results'.format(results.size, results.totalSize))
            self.btn_query_more.setDisabled(results.done)
        except Exception as e:
            self.error_message.setText(str(e))
            self.error_message.show()

    def clear_table(self):
        self.table_s.clear_data()

    def select_table(self):
        table_name = self.table_list.currentItem().text()
        fields = sorted(self.sf_con.get_table_fields(table_name))
        self.txt_query.setText('SELECT {0} FROM {1}'.format(', '.join(fields), table_name))

    def filter_tables(self):
        filter = self.table_searchbox.text()
        table_names = (name for name in self.sf_con.get_tables() if filter.lower() in name.lower())
        while self.table_list.count() > 0:
            self.table_list.takeItem(0)

        for name in table_names:
            self.table_list.addItem(QListWidgetItem(name))
