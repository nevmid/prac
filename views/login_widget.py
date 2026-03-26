from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db.database import Database
from models.user import User
from views.captcha_widget import CaptchaWidget

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.failed_attempts = 0
        self.captcha_passed = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Авторизация - Молочный комбинат 'Полесье'")
        self.setFixedSize(500, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("Авторизация")
        title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #fffafa;
                border: 1px solid black;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel{
                border: None;
                padding: 0px;
            }
            QLineEdit{
                font: 16px;
                font-family: Arial;
                border: 1px solid black;
                border-radius: 5px;
                padding: 3px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)

        login_label = QLabel("Логин:")
        login_label.setFont(QFont("Arial", 10))
        form_layout.addWidget(login_label)
        self.login_lineEdit = QLineEdit()
        self.login_lineEdit.setPlaceholderText("Введите логин")
        form_layout.addWidget(self.login_lineEdit)

        password_label = QLabel("Пароль:")
        password_label.setFont(QFont("Arial", 10))
        form_layout.addWidget(password_label)
        self.password_lineEdit = QLineEdit()
        self.password_lineEdit.setPlaceholderText("Введите пароль")
        self.password_lineEdit.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_lineEdit)
        main_layout.addWidget(form_frame)

        captcha_label = QLabel("Соберите пазл для подтверждения:")
        captcha_label.setAlignment(Qt.AlignCenter)
        captcha_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(captcha_label)

        self.captcha_widget = CaptchaWidget()
        self.captcha_widget.captcha_completed.connect(self.on_captcha_complete)
        main_layout.addWidget(self.captcha_widget, alignment=Qt.AlignCenter)

        self.login_btn = QPushButton("Войти")
        self.login_btn.setEnabled(False)
        self.login_btn.setMinimumSize(200, 50)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        main_layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)


    def on_captcha_complete(self, success):
        self.captcha_passed = success
        self.login_btn.setEnabled(success)

    def login(self):
        login = self.login_lineEdit.text().strip()
        password = self.password_lineEdit.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка",
                                "Пожалуйста, заполните все поля!")
            return


        user = self.db.get_user_by_login(login)

        if not user:
            QMessageBox.warning(
                self,
                "Ошибка авторизации",
                "Вы ввели неверный логин или пароль. "
                "Пожалуйста проверьте ещё раз введенные данные."
            )
            return

        if user['is_blocked']:
            QMessageBox.critical(
                self,
                "Доступ заблокирован",
                "Вы заблокированы. Обратитесь к администратору."
            )
            return

        if password != user['password']:
            self.failed_attempts += 1
            new_attempts = user['failed_attempts'] + 1

            self.db.update_failed_attempts(user['id_user'], new_attempts)

            if new_attempts >= 3:
                self.db.block_user(user['id_user'])
                QMessageBox.critical(
                    self,
                    "Доступ заблокирован",
                    "Вы заблокированы. Обратитесь к администратору."
                )
                return

            QMessageBox.warning(
                self,
                "Ошибка авторизации",
                f"Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные.\n"
            )
            return

        self.db.reset_failed_attempts(user['id_user'])
        self.current_user = User(
            user['id_user'],
            user['login'],
            user['role'],
            user['is_blocked']
        )

        QMessageBox.information(
            self,
            "Успех",
            f"Вы успешно авторизовались!"
        )

        self.open_main_window()

    def open_main_window(self):
        if self.current_user.role == 'user':
            from views.user_window import UserWindow
            self.user_window = UserWindow(self.current_user, self.db)
            self.user_window.show()
        else:
            from views.admin_window import AdminWindow
            self.admin_window = AdminWindow(self.current_user, self.db)
            self.admin_window.show()
        self.close()