import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QRegExp, Qt


class ResultsTable(qtw.QTableWidget):
    def __init__(self, *args, parent=None):
        super(ResultsTable, self).__init__(parent)
        self.setSortingEnabled(True)
        self.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
        self.clipboard = qtg.QGuiApplication.clipboard()

        if len(args) >= 2:
            self.set_data(args[0], args[1])

    def set_data(self, headers, rows):
        self.clear_data()

        self.setColumnCount(len(headers))
        self.setRowCount(len(rows))
        self.setHorizontalHeaderLabels(headers)
        self.resizeColumnsToContents()

        for row_i, row in enumerate(rows):
            for col_i, col in enumerate(row):
                item = qtw.QTableWidgetItem(col)
                self.setItem(row_i, col_i, item)

    def clear_data(self):
        while self.columnCount() > 0:
            self.removeColumn(0)
        while self.rowCount() > 0:
            self.removeRow(0)


class SOQLHighlighter(qtg.QSyntaxHighlighter):

    def __init__(self, parent=None):
        keywords = ['and', 'asc', 'desc', 'excludes', 'first', 'from', 'group', 'having', 'in', 'includes', 'last',
                    'like', 'limit', 'not', 'null', 'nulls', 'or', 'select', 'where', 'with']
        symbols = list('-=,') + r'\[,\],\(,\),!='.split(',')
        quote_regex = r"'[^'\\]*(\\.[^'\\]*)*('|$)"

        super(SOQLHighlighter, self).__init__(parent)

        keyword_format = qtg.QTextCharFormat()
        keyword_format.setForeground(Qt.blue)
        keyword_format.setFontWeight(qtg.QFont.Bold)

        symbol_format = qtg.QTextCharFormat()
        symbol_format.setForeground(Qt.red)

        quote_format = qtg.QTextCharFormat()
        quote_format.setForeground(Qt.darkCyan)

        keyword_patterns = ['\\b{0}\\b'.format(word) for word in keywords]
        self.highlight_rules = [(QRegExp(pattern, Qt.CaseInsensitive), keyword_format) for pattern in keyword_patterns]
        self.highlight_rules.extend((QRegExp(pattern), symbol_format) for pattern in symbols)
        self.highlight_rules.append((QRegExp(quote_regex), quote_format))

    def highlightBlock(self, text):
        for pattern, frmt in self.highlight_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, frmt)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


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
