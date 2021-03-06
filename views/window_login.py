import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import Qt

from models.salesforce_connector import SForceConnector
from utils import utils


class LoginWindow(qtw.QDialog):

    def __init__(self, parent=None, saved_logins: dict = {}):
        super().__init__(parent)

        self.sf_con = None
        self.saved_logins = saved_logins

        self.saved_logins[''] = {
            'username': '',
            'password': '',
            'sandbox': False,
            'security_token': ''
        }

        self.lbl_saved_logins = qtw.QLabel('Saved Logins:')
        self.lbl_username = qtw.QLabel('Username:')
        self.lbl_password = qtw.QLabel('Password:')
        self.lbl_environment = qtw.QLabel('Environment:')
        self.lbl_security_token = qtw.QLabel('Security Token (Optional):')
        self.cmb_saved_logins = qtw.QComboBox()
        self.cmb_environment = qtw.QComboBox()
        self.txt_username = qtw.QLineEdit()
        self.txt_password = qtw.QLineEdit()
        self.txt_security_token = qtw.QLineEdit()
        self.btn_login = qtw.QPushButton('Login')
        self.btn_save = qtw.QPushButton('Save Credentials')
        self.btn_exit = qtw.QPushButton('Exit')

        self.setWindowTitle('SalesForce Viewer')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.txt_password.setEchoMode(qtw.QLineEdit.Password)
        self.cmb_saved_logins.addItems(sorted(saved_logins.keys()))
        self.cmb_environment.addItems(['Production', 'Sandbox'])

        self.btn_login.clicked.connect(self._handle_login)
        self.btn_save.clicked.connect(self._save_login)
        self.btn_exit.clicked.connect(self.reject)
        self.cmb_saved_logins.currentIndexChanged.connect(self._select_saved_login)

        self._root_layout = qtw.QGridLayout(self)

        row_count = 0
        self._root_layout.addWidget(self.lbl_saved_logins, row_count, 0, 1, 1)
        self._root_layout.addWidget(self.cmb_saved_logins, row_count, 1, 1, 2)
        row_count += 1
        self._root_layout.addWidget(self.lbl_username, row_count, 0, 1, 1)
        self._root_layout.addWidget(self.txt_username, row_count, 1, 1, 2)
        row_count += 1
        self._root_layout.addWidget(self.lbl_password, row_count, 0, 1, 1)
        self._root_layout.addWidget(self.txt_password, row_count, 1, 1, 2)
        row_count += 1
        self._root_layout.addWidget(self.lbl_environment, row_count, 0, 1, 1)
        self._root_layout.addWidget(self.cmb_environment, row_count, 1, 1, 2)
        row_count += 1
        self._root_layout.addWidget(self.lbl_security_token, row_count, 0, 1, 1)
        self._root_layout.addWidget(self.txt_security_token, row_count, 1, 1, 2)
        row_count += 1
        self._root_layout.addWidget(self.btn_login, row_count, 0, 1, 1)
        self._root_layout.addWidget(self.btn_save, row_count, 1, 1, 1)
        self._root_layout.addWidget(self.btn_exit, row_count, 2, 1, 1)

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
            qtw.QMessageBox.warning(self, 'Error', str(ex))

    def get_login(self):
        return self.sf_con