from functools import partial
import traceback

import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt

from utils.custom_widgets import SOQLHighlighter, ResultsTable, FindDialog


def _table_selection_to_text(table: ResultsTable, include_headers=False):
    if not table.selectedRanges():
        return

    selected = table.selectedRanges()[0]

    top_row = selected.topRow()
    bottom_row = selected.bottomRow()
    left_col = selected.leftColumn()
    right_col = selected.rightColumn()

    rows = []
    if include_headers:
        rows.append([table.horizontalHeaderItem(i).text() for i in range(left_col, right_col + 1)])

    for row in range(top_row, bottom_row + 1):
        columns = []
        for col in range(left_col, right_col + 1):
            columns.append(table.item(row, col).text().replace('\t', ' '))
        rows.append(columns)
    text = '\n'.join('\t'.join(cols) for cols in rows)
    return text


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
        self._frm_buttons = qtw.QFrame()
        self._layout_nw = qtw.QVBoxLayout()
        self._layout_ne = qtw.QVBoxLayout()
        self._layout_buttons = qtw.QHBoxLayout()
        self._txt_query = qtw.QTextEdit()
        self._tbl_s = ResultsTable()
        self._splitter_h = qtw.QSplitter(Qt.Horizontal)
        self._splitter_v = qtw.QSplitter(Qt.Vertical)
        self._lst_tables = qtw.QListWidget()
        self._txt_filter = qtw.QLineEdit()
        self._syntax_highlighter = SOQLHighlighter(self._txt_query)
        self._status_bar = qtw.QStatusBar()
        self._lbl_status = qtw.QLabel(self)

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
        self._layout_ne.addLayout(self._layout_buttons)
        self._layout_buttons.addWidget(self._btn_query)
        self._layout_buttons.addWidget(self._btn_query_more)
        self._txt_query.setFrameShape(qtw.QFrame.StyledPanel)
        self._btn_query_more.setDisabled(True)

        # Bottom
        self._tbl_s.setFrameShape(qtw.QFrame.StyledPanel)
        self.setStatusBar(self._status_bar)
        self._status_bar.addPermanentWidget(self._lbl_status)

        # Splitters
        self._splitter_h.addWidget(self._frm_nw)
        self._splitter_h.addWidget(self._frm_ne)
        self._splitter_v.addWidget(self._splitter_h)
        self._splitter_v.addWidget(self._tbl_s)
        self._splitter_h.setSizes([100, 50])
        self._splitter_v.setSizes([100, 50])

        # Root
        self.setCentralWidget(self._root_frame)
        self._root_layout.addWidget(self._splitter_v)
        self._root_frame.setLayout(self._root_layout)

        # Finalize
        self.setWindowTitle('SalesForce Viewer')

        # Install Event Filters
        self._txt_query.installEventFilter(self)
        self._tbl_s.installEventFilter(self)
        self._lst_tables.installEventFilter(self)

        # Event Functions
        self._event_callbacks = {}

        # Other
        self._clipboard = qtg.QGuiApplication.clipboard()
        self._find_dialog = FindDialog(self._syntax_highlighter)

    def set_listener_run_query(self, func):
        self._btn_query.clicked.connect(func)
        self._event_callbacks['run_query'] = func

    def set_listener_query_more(self, func):
        self._btn_query_more.clicked.connect(func)
        self._event_callbacks['query_more'] = func

    def set_listener_table_selected(self, func):
        self._lst_tables.doubleClicked.connect(func)
        self._event_callbacks['table_selected'] = func

    def set_listener_filter_tables(self, func):
        self._txt_filter.textChanged.connect(func)
        self._event_callbacks['filter_tables'] = func

    def eventFilter(self, source, event):
        # Key Press Event on Query Text Box
        if source == self._txt_query and event.type() == QEvent.KeyPress:
            # Ctrl+Enter
            if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Return:
                self._event_callbacks['run_query']()
                return True

            # Ctrl+F
            elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F:
                self._find_dialog.show()
                return True

        # Enter Pressed in Table List
        elif source == self._lst_tables and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return:
                self._event_callbacks['table_selected']()
                return True

        # Key Press Event on Results Table
        elif source == self._tbl_s and event.type() == QEvent.KeyPress:
            if event.modifiers() & Qt.ControlModifier:
                if event.key() == Qt.Key_A:
                    self._tbl_s.selectAll()
                    return True
                elif event.key() == Qt.Key_C:
                    self.copy_selected_cells(False)
                    return True

        # Right Click on Results Table
        elif source == self._tbl_s and event.type() == QEvent.ContextMenu:
            menu = qtw.QMenu(self)
            select_all = qtw.QAction('Select All (Ctrl+A)', self)
            copy_no_headers = qtw.QAction('Copy Cells (Ctrl+C)', self)
            copy_headers = qtw.QAction('Copy Cells With Headers', self)
            menu.addAction(select_all)
            menu.addAction(copy_no_headers)
            menu.addAction(copy_headers)

            select_all.triggered.connect(source.selectAll)
            copy_no_headers.triggered.connect(partial(self.copy_selected_cells, False))
            copy_headers.triggered.connect(partial(self.copy_selected_cells, True))

            menu.popup(qtg.QCursor.pos())

        return qtw.QMainWindow.eventFilter(self, source, event)

    def copy_selected_cells(self, include_headers=False):
        self._clipboard.setText(_table_selection_to_text(self._tbl_s, include_headers))
        self.temp_status_text = 'Cells Copied To Clipboard'

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
        self.temp_status_text = 'Available Tables: {0}'.format(self._lst_tables.count())

    @property
    def query_text(self):
        return self._txt_query.toPlainText()

    @query_text.setter
    def query_text(self, text):
        self._txt_query.setText(text)
        self.temp_status_text = 'Query Text Updated'

    @property
    def status_text(self):
        return self._lbl_status.text()

    @status_text.setter
    def status_text(self, text):
        self._lbl_status.setText(text)

    @property
    def temp_status_text(self):
        return self._status_bar.currentMessage()

    @temp_status_text.setter
    def temp_status_text(self, text):
        self._status_bar.showMessage(text, 1000)

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
        self.temp_status_text = 'Results Updated: {0} Columns, {1} Rows'.format(len(headers), len(rows))
