from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

import utils
from models.salesforce_connector import SForceConnector


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

        self.lbl_saved_logins = QLabel('Saved Logins:')
        self.lbl_username = QLabel('Username:')
        self.lbl_password = QLabel('Password:')
        self.lbl_environment = QLabel('Environment:')
        self.lbl_security_token = QLabel('Security Token (Optional):')
        self.cmb_saved_logins = QComboBox()
        self.cmb_environment = QComboBox()
        self.txt_username = QLineEdit()
        self.txt_password = QLineEdit()
        self.txt_security_token = QLineEdit()
        self.btn_login = QPushButton('Login')
        self.btn_save = QPushButton('Save Credentials')
        self.btn_exit = QPushButton('Exit')

        self.setWindowTitle('SalesForce Viewer')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.cmb_saved_logins.addItems(sorted(saved_logins.keys()))
        self.cmb_environment.addItems(['Production', 'Sandbox'])
        self.btn_exit.setStyleSheet('background-color: red')

        self.btn_login.clicked.connect(self._handle_login)
        self.btn_save.clicked.connect(self._save_login)
        self.btn_exit.clicked.connect(self.reject)
        self.cmb_saved_logins.currentIndexChanged.connect(self._select_saved_login)

        layout = QGridLayout(self)

        layout.addWidget(self.lbl_saved_logins, row_count, 0, 1, 1)
        layout.addWidget(self.cmb_saved_logins, row_count, 1, 1, 2)
        row_count += 1
        layout.addWidget(self.lbl_username, row_count, 0, 1, 1)
        layout.addWidget(self.txt_username, row_count, 1, 1, 2)
        row_count += 1
        layout.addWidget(self.lbl_password, row_count, 0, 1, 1)
        layout.addWidget(self.txt_password, row_count, 1, 1, 2)
        row_count += 1
        layout.addWidget(self.lbl_environment, row_count, 0, 1, 1)
        layout.addWidget(self.cmb_environment, row_count, 1, 1, 2)
        row_count += 1
        layout.addWidget(self.lbl_security_token, row_count, 0, 1, 1)
        layout.addWidget(self.txt_security_token, row_count, 1, 1, 2)
        row_count += 1
        layout.addWidget(self.btn_login, row_count, 0, 1, 1)
        layout.addWidget(self.btn_save, row_count, 1, 1, 1)
        layout.addWidget(self.btn_exit, row_count, 2, 1, 1)

    def _save_login(self):
        username = self.txt_username.text()
        password = self.txt_password.text()
        sandbox = True if self.cmb_environment.currentText() == 'Sandbox' else False
        security_token = self.txt_security_token.text()
        name = '{0} - {1}'.format('SANDBOX' if sandbox else 'PROD', username)

        self.saved_logins[name] = {
            'username': username,
            'password': password,
            'sandbox': sandbox,
            'security_token': security_token
        }

        utils.save_config(self.saved_logins)

        while self.cmb_saved_logins.count() > 0:
            self.cmb_saved_logins.removeItem(0)
        self.cmb_saved_logins.addItems(self.saved_logins)

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