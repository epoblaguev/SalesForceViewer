import re

import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QRegExp, Qt


class ResultsTable(qtw.QTableWidget):
    def __init__(self, *args, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        if len(args) >= 2:
            self.set_data(args[0], args[1])

    def set_data(self, headers, rows):
        self.clear_data()

        self.setColumnCount(len(headers))
        self.setRowCount(len(rows))
        self.setHorizontalHeaderLabels(headers)

        for row_i, row in enumerate(rows):
            for col_i, col in enumerate(row):
                item = qtw.QTableWidgetItem(col)
                self.setItem(row_i, col_i, item)

        self.resizeColumnsToContents()
        for col_i in range(self.columnCount()):
            if self.columnWidth(col_i) > (self.width() / 4):
                self.setColumnWidth(col_i, self.width() / 4)

    def clear_data(self):
        while self.columnCount() > 0:
            self.removeColumn(0)
        while self.rowCount() > 0:
            self.removeRow(0)


class SOQLHighlighter(qtg.QSyntaxHighlighter):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.keywords = ['and', 'asc', 'desc', 'excludes', 'first', 'from', 'group', 'having', 'in', 'includes', 'last',
                    'like', 'limit', 'not', 'null', 'nulls', 'or', 'select', 'where', 'with']
        self.symbols = list('-=,') + r'\[,\],\(,\),!='.split(',')
        self.quote_regex = r"'[^'\\]*(\\.[^'\\]*)*('|$)"

        self.search_text = None

        self.keyword_format = qtg.QTextCharFormat()
        self.keyword_format.setForeground(Qt.blue)
        self.keyword_format.setFontWeight(qtg.QFont.Bold)

        self.symbol_format = qtg.QTextCharFormat()
        self.symbol_format.setForeground(Qt.red)

        self.quote_format = qtg.QTextCharFormat()
        self.quote_format.setForeground(Qt.darkCyan)

        self.search_format = qtg.QTextCharFormat()
        self.search_format.setBackground(Qt.green)

        self.keyword_patterns = ['\\b{0}\\b'.format(word) for word in self.keywords]
        self.highlight_rules = []
        self._update_highlight_rules()

    def find(self, text):
        self.search_text = text
        self._update_highlight_rules()

    def _update_highlight_rules(self):
        self.highlight_rules = [(QRegExp(pattern, Qt.CaseInsensitive), self.keyword_format) for pattern in
                                self.keyword_patterns]
        self.highlight_rules.extend((QRegExp(pattern), self.symbol_format) for pattern in self.symbols)
        self.highlight_rules.append((QRegExp(self.quote_regex), self.quote_format))
        if self.search_text not in (None, ''):
            self.highlight_rules.append((QRegExp(self.search_text, Qt.CaseInsensitive), self.search_format))

    def highlightBlock(self, text):
        for pattern, frmt in self.highlight_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, frmt)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


class FindDialog(qtw.QDialog):
    def __init__(self, find_area: SOQLHighlighter, parent=None):
        super().__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.setWindowTitle('Find Text')

        self._find_area = find_area

        self._txt_find = qtw.QLineEdit()
        self._btn_close = qtw.QPushButton('Close')

        self._root_layout = qtw.QVBoxLayout(self)
        self._root_layout.addWidget(self._txt_find)
        self._root_layout.addWidget(self._btn_close)

        self._txt_find.textChanged.connect(self._find)
        self._btn_close.clicked.connect(self.close)
        self._txt_find.setFocus()

    def closeEvent(self, event):
        self._txt_find.setText('')
        self._find_area.find(None)
        self._find_area.rehighlight()

    def _find(self):
        text = re.escape(self._txt_find.text())
        self._find_area.find(text)
        self._find_area.rehighlight()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import *

    app = QApplication(sys.argv)

    window = QMainWindow()
    layout = QVBoxLayout()

    window.setLayout(layout)
    editor = QTextEdit(window)
    layout.addWidget(editor)

    highlighter = SOQLHighlighter(editor)
    window.show()
    sys.exit(app.exec_())
