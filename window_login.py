from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from salesforce_connector import SForceConnector


class LoginWindow(QDialog):

    def __init__(self, parent=None, saved_logins: dict = {}):
        super(LoginWindow, self).__init__(parent)

        row_count = 0

        self.sf_con = None
        self.saved_logins = saved_logins

        self.saved_logins[''] = {
            'username': '',
            'password': '',
            'sandbox': False,
            'security_token': ''
        }

        self.lbl_saved_logins = QLabel(self)
        self.lbl_username = QLabel(self)
        self.lbl_password = QLabel(self)
        self.lbl_environment = QLabel(self)
        self.lbl_security_token = QLabel(self)
        self.cmb_saved_logins = QComboBox(self)
        self.txt_username = QLineEdit(self)
        self.txt_password = QLineEdit(self)
        self.cmb_environment = QComboBox(self)
        self.txt_security_token = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)

        self.setWindowTitle('SalesForce Viewer')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.lbl_saved_logins.setText('Saved Logins:')
        self.lbl_username.setText('Username:')
        self.lbl_password.setText('Password:')
        self.lbl_environment.setText('Environment:')
        self.lbl_security_token.setText('Security Token (Optinoal):')
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.buttonLogin.clicked.connect(self._handle_login)
        self.cmb_saved_logins.addItems(sorted(saved_logins.keys()))
        self.cmb_saved_logins.currentIndexChanged.connect(self._select_saved_login)
        self.cmb_environment.addItems(['Production', 'Sandbox'])

        layout = QGridLayout(self)

        layout.addWidget(self.lbl_saved_logins, row_count, 0)
        layout.addWidget(self.cmb_saved_logins, row_count, 1)
        row_count += 1
        layout.addWidget(self.lbl_username, row_count, 0)
        layout.addWidget(self.txt_username, row_count, 1)
        row_count += 1
        layout.addWidget(self.lbl_password, row_count, 0)
        layout.addWidget(self.txt_password, row_count, 1)
        row_count += 1
        layout.addWidget(self.lbl_environment, row_count, 0)
        layout.addWidget(self.cmb_environment, row_count, 1)
        row_count += 1
        layout.addWidget(self.lbl_security_token, row_count, 0)
        layout.addWidget(self.txt_security_token, row_count, 1)
        row_count += 1
        layout.addWidget(self.buttonLogin, row_count, 0, 1, 2)

    def _select_saved_login(self):
        current_value = self.cmb_saved_logins.currentText()
        credentials = self.saved_logins[current_value]
        self.txt_username.setText(credentials['username'])
        self.txt_password.setText(credentials['password'])
        self.cmb_environment.setCurrentText('Sandbox' if credentials['sandbox'] else 'Production')
        self.txt_security_token.setText(credentials['security_token'])

    def _handle_login(self):
        username = self.txt_username.text()
        password = self.txt_password.text()
        environment = True if self.cmb_environment.currentText() == 'Sandbox' else False

        try:
            self.sf_con = SForceConnector(username, password, environment)
            self.accept()
        except Exception as ex:
            QMessageBox.warning(self, 'Error', str(ex))

    def get_login(self):
        return self.sf_con