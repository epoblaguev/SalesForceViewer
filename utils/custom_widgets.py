from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QGuiApplication


class ResultsTable(QTableWidget):
    def __init__(self, *args):
        QTableWidget.__init__(self)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clipboard = QGuiApplication.clipboard()

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
                item = QTableWidgetItem(col)
                self.setItem(row_i, col_i, item)

    def clear_data(self):
        while self.columnCount() > 0:
            self.removeColumn(0)
        while self.rowCount() > 0:
            self.removeRow(0)

    def keyPressEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:  # Control Modifier

            if e.key() == Qt.Key_C:  # Copy Selected Range
                selected = self.selectedRanges()[0]

                rows = []
                for row in range(selected.topRow(), selected.bottomRow() + 1):
                    columns = []
                    for col in range(selected.leftColumn(), selected.rightColumn() + 1):
                        columns.append(self.item(row, col).text().replace('\t', ' '))
                    rows.append(columns)
                text = '\n'.join('\t'.join(cols) for cols in rows)
                self.clipboard.setText(text)


class SOQLHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        keywords = ['and', 'asc', 'desc', 'excludes', 'first', 'from', 'group', 'having', 'in', 'includes', 'last',
                    'like', 'limit', 'not', 'null', 'nulls', 'or', 'select', 'where', 'with']
        symbols = list('-=,') + r'\[,\],\(,\)'.split(',')+['"', "'"]

        super(SOQLHighlighter, self).__init__(parent)

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.blue)
        keyword_format.setFontWeight(QFont.Bold)

        symbol_format = QTextCharFormat()
        symbol_format.setForeground(Qt.red)

        keyword_patterns = ['\\b{0}\\b'.format(word) for word in keywords]
        self.highlightingRules = [(QRegExp(pattern, Qt.CaseInsensitive), keyword_format) for pattern in keyword_patterns]
        self.highlightingRules.extend((QRegExp(pattern, Qt.CaseInsensitive), symbol_format) for pattern in symbols)

    def highlightBlock(self, text):
        for pattern, frmt in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, frmt)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
