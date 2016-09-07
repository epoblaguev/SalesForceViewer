import sys

from PyQt5.QtWidgets import QApplication, QDialog

from controllers.main_controller import MainController
from utils import utils
from views.window_login import LoginWindow
from views.window_main import MainWindow

if __name__ == '__main__':
    logins = utils.load_config()

    app = QApplication(sys.argv)

    login = LoginWindow(saved_logins=logins)

    if login.exec_() == QDialog.Accepted:
        sf_con = login.get_login()
        window = MainWindow()
        controller = MainController(window, sf_con)
        controller.show()
        sys.exit(app.exec_())
