from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from utils.custom_widgets import SOQLHighlighter, ResultsTable


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Popups
        self.error_message = QMessageBox()
        self.error_message.setIcon(QMessageBox.Warning)

        # INIT ELEMENTS
        self.root_frame = QFrame()
        self.root_layout = QHBoxLayout()
        self.btn_query = QPushButton('Run Query')
        self.btn_query_more = QPushButton('Query More')
        self.frm_nw = QFrame()
        self.frm_ne = QFrame()
        self.layout_nw = QVBoxLayout()
        self.layout_ne = QVBoxLayout()
        self.txt_query = QTextEdit()
        self.tbl_s = ResultsTable()
        self.splitter_h = QSplitter(Qt.Horizontal)
        self.splitter_v = QSplitter(Qt.Vertical)
        self.lst_tables = QListWidget()
        self.txt_filter = QLineEdit()
        self.syntax_highlighter = SOQLHighlighter(self.txt_query)
        self.status_bar = QStatusBar()

        # --- ARRANGE ELEMENTS ---

        # Top Left
        self.frm_nw.setFrameShape(QFrame.StyledPanel)
        self.frm_nw.setLayout(self.layout_nw)
        self.layout_nw.addWidget(self.txt_filter)
        self.layout_nw.addWidget(self.lst_tables)
        self.txt_filter.setPlaceholderText('Filter Tables')

        # Top Right
        self.frm_ne.setFrameShape(QFrame.StyledPanel)
        self.frm_ne.setLayout(self.layout_ne)
        self.layout_ne.addWidget(self.txt_query)
        self.layout_ne.addWidget(self.btn_query)
        self.layout_ne.addWidget(self.btn_query_more)
        self.txt_query.setFrameShape(QFrame.StyledPanel)
        self.btn_query_more.setDisabled(True)

        # Bottom
        self.tbl_s.setFrameShape(QFrame.StyledPanel)
        self.setStatusBar(self.status_bar)

        # Splitters
        self.splitter_h.addWidget(self.frm_nw)
        self.splitter_h.addWidget(self.frm_ne)
        self.splitter_v.addWidget(self.splitter_h)
        self.splitter_v.addWidget(self.tbl_s)

        # Root
        self.setCentralWidget(self.root_frame)
        self.root_layout.addWidget(self.splitter_v)
        self.root_frame.setLayout(self.root_layout)

        # Finalize
        self.setWindowTitle('SalesForce Viewer')

    def set_listener_run_query(self, func):
        self.btn_query.clicked.connect(func)

    def set_listener_query_more(self, func):
        self.btn_query_more.clicked.connect(func)

    def set_listener_table_selected(self, func):
        self.lst_tables.doubleClicked.connect(func)

    def set_listener_filter_tables(self, func):
        self.txt_filter.textChanged.connect(func)

    def get_filter_text(self):
        return self.txt_filter.text()

    def get_selected_table(self):
        return self.lst_tables.currentItem().text()

    def get_query_text(self):
        return self.txt_query.toPlainText()

    def update_results_table(self, headers: list, rows: list):
        self.tbl_s.set_data(headers, rows)

    def update_query_status(self, size: int, total_size: int):
        self.status_bar.showMessage('{0} / {1} Results'.format(size, total_size))
        self.btn_query_more.setEnabled(size < total_size)

    def update_query_text(self, text):
        self.txt_query.setText(text)

    def update_table_list(self, table_names: iter):
        while self.lst_tables.count() > 0:
            self.lst_tables.takeItem(0)
        for name in table_names:
            self.lst_tables.addItem(QListWidgetItem(name))

    def display_error_message(self, text):
        self.error_message.setText(text)
        self.error_message.show()