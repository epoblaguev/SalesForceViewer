from PyQt5.QtWidgets import QApplication, QDialog
from window_login import LoginWindow
from window_main import MainWindow
import utils

if __name__ == '__main__':
    logins = utils.load_config()

    import sys

    app = QApplication(sys.argv)
    login = LoginWindow(saved_logins=logins)

    if login.exec_() == QDialog.Accepted:
        sf_con = login.get_login()
        window = MainWindow(sf_con)
        window.show()
        sys.exit(app.exec_())
