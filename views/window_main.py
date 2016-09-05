import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import Qt

from utils.custom_widgets import SOQLHighlighter, ResultsTable


class MainWindow(qtw.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Popups
        self._error_message = qtw.QMessageBox()
        self._error_message.setIcon(qtw.QMessageBox.Warning)

        # INIT ELEMENTS
        self._root_frame = qtw.QFrame()
        self._root_layout = qtw.QHBoxLayout()
        self._btn_query = qtw.QPushButton('Run Query')
        self._btn_query_more = qtw.QPushButton('Query More')
        self._frm_nw = qtw.QFrame()
        self._frm_ne = qtw.QFrame()
        self._layout_nw = qtw.QVBoxLayout()
        self._layout_ne = qtw.QVBoxLayout()
        self._txt_query = qtw.QTextEdit()
        self._tbl_s = ResultsTable()
        self._splitter_h = qtw.QSplitter(Qt.Horizontal)
        self._splitter_v = qtw.QSplitter(Qt.Vertical)
        self._lst_tables = qtw.QListWidget()
        self._txt_filter = qtw.QLineEdit()
        self._syntax_highlighter = SOQLHighlighter(self._txt_query)
        self._status_bar = qtw.QStatusBar()

        # --- ARRANGE ELEMENTS ---

        # Top Left
        self._frm_nw.setFrameShape(qtw.QFrame.StyledPanel)
        self._frm_nw.setLayout(self._layout_nw)
        self._layout_nw.addWidget(self._txt_filter)
        self._layout_nw.addWidget(self._lst_tables)
        self._txt_filter.setPlaceholderText('Filter Tables')

        # Top Right
        self._frm_ne.setFrameShape(qtw.QFrame.StyledPanel)
        self._frm_ne.setLayout(self._layout_ne)
        self._layout_ne.addWidget(self._txt_query)
        self._layout_ne.addWidget(self._btn_query)
        self._layout_ne.addWidget(self._btn_query_more)
        self._txt_query.setFrameShape(qtw.QFrame.StyledPanel)
        self._btn_query_more.setDisabled(True)

        # Bottom
        self._tbl_s.setFrameShape(qtw.QFrame.StyledPanel)
        self.setStatusBar(self._status_bar)

        # Splitters
        self._splitter_h.addWidget(self._frm_nw)
        self._splitter_h.addWidget(self._frm_ne)
        self._splitter_v.addWidget(self._splitter_h)
        self._splitter_v.addWidget(self._tbl_s)

        # Root
        self.setCentralWidget(self._root_frame)
        self._root_layout.addWidget(self._splitter_v)
        self._root_frame.setLayout(self._root_layout)

        # Finalize
        self.setWindowTitle('SalesForce Viewer')

    def listener_run_query(self, func):
        self._btn_query.clicked.connect(func)

    def set_listener_run_query(self, func):
        self._btn_query.clicked.connect(func)

    def set_listener_query_more(self, func):
        self._btn_query_more.clicked.connect(func)

    def set_listener_table_selected(self, func):
        self._lst_tables.doubleClicked.connect(func)

    def set_listener_filter_tables(self, func):
        self._txt_filter.textChanged.connect(func)

    @property
    def filter_text(self):
        return self._txt_filter.text()

    @filter_text.setter
    def filter_text(self, text):
        self._txt_filter.setText(text)

    @property
    def selected_table(self):
        return self._lst_tables.currentItem().text()

    @property
    def tables(self):
        return [item.text() for item in self._lst_tables.items()]

    @tables.setter
    def tables(self, table_names: list):
        while self._lst_tables.count() > 0:
            self._lst_tables.takeItem(0)
        for name in table_names:
            self._lst_tables.addItem(qtw.QListWidgetItem(name))

    @property
    def query_text(self):
        return self._txt_query.toPlainText()

    @query_text.setter
    def query_text(self, text):
        self._txt_query.setText(text)

    @property
    def status_text(self):
        return self._status_bar.currentMessage()

    @status_text.setter
    def status_text(self, text):
        self._status_bar.showMessage(text)

    @property
    def query_more_enabled(self) -> bool:
        return self._btn_query_more.isEnabled()

    @query_more_enabled.setter
    def query_more_enabled(self, enabled: bool):
        self._btn_query_more.setEnabled(enabled)

    @property
    def error_message(self):
        return self._error_message.text()

    @error_message.setter
    def error_message(self, text):
        self._error_message.setText(text)
        self._error_message.show()

    def update_results_table(self, headers: list, rows: list):
        self._tbl_s.set_data(headers, rows)
