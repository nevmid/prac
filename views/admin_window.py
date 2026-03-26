from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QDialog, QFormLayout, QLineEdit, QComboBox,
                             QMessageBox, QHeaderView, QCheckBox, QFocusFrame, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class UserDialog(QDialog):
    def __init__(self, db, user=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.setWindowTitle("Пользователь" if not user else "Редактирование пользователя")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.login_edit = QLineEdit()
        if self.user:
            self.login_edit.setText(self.user['login'])
        layout.addRow("Логин:", self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("Пароль:", self.password_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        if self.user:
            index = self.role_combo.findText(self.user['role'])
            self.role_combo.setCurrentIndex(index)
        layout.addRow("Роль:", self.role_combo)

        self.blocked_check = QCheckBox("Заблокирован")
        if self.user:
            self.blocked_check.setChecked(self.user['is_blocked'])
        layout.addRow(self.blocked_check)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def save(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()
        role = self.role_combo.currentText()
        is_blocked = self.blocked_check.isChecked()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if not self.user:
            existing = self.db.get_user_by_login(login)
            if existing:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Пользователь с таким логином уже существует!"
                )
                return

            result = self.db.create_user(login, password, role)
            if result:
                QMessageBox.information(self, "Успех", "Пользователь добавлен!")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить пользователя")
        else:
            result = self.db.update_user(
                self.user['id_user'], login, password, role, is_blocked
            )
            if result:
                QMessageBox.information(self, "Успех", "Данные обновлены!")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить данные")


class AdminWindow(QMainWindow):
    def __init__(self, current_user, db):
        super().__init__()
        self.current_user = current_user
        self.db = db
        self.setWindowTitle("Администрирование")
        self.setMinimumSize(800, 500)
        self.init_ui()
        self.load_customers()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: #fffafa;
                border: 1px solid black;
                border-radius: 10px;
            }
        """)
        frame_layout = QHBoxLayout(main_frame)
        btns_frame = QFrame()
        btns_frame.setStyleSheet("""
            QFrame{
            background-color: #fffafa;
            border: None
            }
        """)
        btns_layout = QVBoxLayout(btns_frame)
        self.customer_btn = QPushButton("Заказчики")
        self.customer_btn.clicked.connect(self.load_customers)
        self.order_btn = QPushButton("Заказы")
        self.order_btn.clicked.connect(self.load_orders)
        self.specification_btn = QPushButton("Спецификации")
        self.specification_btn.clicked.connect(self.load_specifications)
        self.material_btn = QPushButton("Материалы")
        self.material_btn.clicked.connect(self.load_materials)
        self.product_btn = QPushButton("Продукция")
        self.product_btn.clicked.connect(self.load_products)
        self.production_btn = QPushButton("Производство")
        self.production_btn.clicked.connect(self.load_productions)
        if self.current_user.role == "admin":
            self.user_btn = QPushButton("Пользователи")
            self.user_btn.clicked.connect(self.load_users)
            btns_layout.addWidget(self.user_btn)

        btns_layout.addWidget(self.customer_btn)
        btns_layout.addWidget(self.order_btn)
        btns_layout.addWidget(self.specification_btn)
        btns_layout.addWidget(self.material_btn)
        btns_layout.addWidget(self.product_btn)
        btns_layout.addWidget(self.production_btn)

        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame{
            background-color: #fffafa;
            border: None
            }
            QTableWidget {
            gridline-color: #ddd;
            }
        """)
        table_layout = QVBoxLayout(table_frame)

        self.main_table = QTableWidget()
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if self.current_user.role == "admin":
            self.add_btn = QPushButton("Добавить пользователя")
            self.add_btn.clicked.connect(self.add_user)
            self.add_btn.hide()

        table_layout.addWidget(self.main_table)
        table_layout.addWidget(self.add_btn, alignment=Qt.AlignCenter)
        btns_layout.setAlignment(Qt.AlignTop)
        frame_layout.addWidget(btns_frame)
        frame_layout.addWidget(table_frame)
        main_layout.addWidget(main_frame)

    def load_customers(self):
        self.main_table.clear()
        self.add_btn.hide()
        customers = self.db.get_customers()
        self.main_table.setColumnCount(7)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Наименование", "ИНН", "Адрес", "Телефон", "Продавец", "Покупатель"])
        self.main_table.setRowCount(len(customers))

        for row, customer in enumerate(customers):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(customer['id_customer'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(customer['name']))
            self.main_table.setItem(row, 2, QTableWidgetItem(customer['inn']))
            self.main_table.setItem(row, 3, QTableWidgetItem(customer['address']))
            self.main_table.setItem(row, 4, QTableWidgetItem(customer['phone']))
            self.main_table.setItem(row, 5,
                                    QTableWidgetItem("Да" if customer['is_salesman'] == True else "Нет"))
            self.main_table.setItem(row, 6,
                                    QTableWidgetItem("Да" if customer['is_buyer'] == True else "Нет"))

    def load_orders(self):
        self.main_table.clear()
        self.add_btn.hide()
        orders = self.db.get_orders()
        self.main_table.setColumnCount(7)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Номер заказа", "Дата заказа", "Заказчик", "Продукция", "Количество", "Цена за единицу продукции"])
        self.main_table.setRowCount(len(orders))

        for row, item in enumerate(orders):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(item['id_order'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(item['order_number']))
            self.main_table.setItem(row, 2, QTableWidgetItem(str(item['order_date'])))
            self.main_table.setItem(row, 3, QTableWidgetItem(str(item['id_customer'])))
            self.main_table.setItem(row, 4, QTableWidgetItem(str(item['id_product'])))
            self.main_table.setItem(row, 5,
                                    QTableWidgetItem(str(item["count"])))
            self.main_table.setItem(row, 6,
                                    QTableWidgetItem(str(item["price_at_order"])))

    def load_specifications(self):
        self.main_table.clear()
        self.add_btn.hide()
        specifications = self.db.get_specifications()
        self.main_table.setColumnCount(5)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Продукция", "Материал", "Норма расхода"])
        self.main_table.setRowCount(len(specifications))

        for row, item in enumerate(specifications):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(item['id_specification'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.main_table.setItem(row, 2, QTableWidgetItem(str(item['id_product'])))
            self.main_table.setItem(row, 3, QTableWidgetItem(str(item['id_material'])))
            self.main_table.setItem(row, 4, QTableWidgetItem(str(item['consumption_rate'])))

    def load_products(self):
        self.main_table.clear()
        self.add_btn.hide()
        products = self.db.get_products()
        self.main_table.setColumnCount(4)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Единица измерения", "Цена за единицу"])
        self.main_table.setRowCount(len(products))

        for row, item in enumerate(products):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(item['id_product'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.main_table.setItem(row, 2, QTableWidgetItem(item['unit']))
            self.main_table.setItem(row, 3, QTableWidgetItem(str(item['current_price'])))

    def load_materials(self):
        self.main_table.clear()
        self.add_btn.hide()
        materials = self.db.get_materials()
        self.main_table.setColumnCount(4)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Единица измерения", "Цена за единицу"])
        self.main_table.setRowCount(len(materials))

        for row, item in enumerate(materials):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(item['id_material'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.main_table.setItem(row, 2, QTableWidgetItem(item['unit']))
            self.main_table.setItem(row, 3, QTableWidgetItem(str(item['current_price'])))

    def load_productions(self):
        self.main_table.clear()
        self.add_btn.hide()
        productions = self.db.get_productions()
        self.main_table.setColumnCount(5)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Номер", "Дата", "Спецификация", "Количество"])
        self.main_table.setRowCount(len(productions))

        for row, item in enumerate(productions):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(item['id_production'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(item['production_number']))
            self.main_table.setItem(row, 2, QTableWidgetItem(str(item['production_date'])))
            self.main_table.setItem(row, 3, QTableWidgetItem(str(item['id_specification'])))
            self.main_table.setItem(row, 4, QTableWidgetItem(str(item['count_produced'])))

    def load_users(self):
        self.main_table.clear()
        self.add_btn.show()
        users = self.db.get_all_users()
        self.main_table.setColumnCount(6)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Логин", "Роль", "Заблокирован", "Попытки", "Действия"])
        self.main_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(user['id_user'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(user['login']))
            self.main_table.setItem(row, 2, QTableWidgetItem(user['role']))
            blocked_text = "Да" if user['is_blocked'] else "Нет"
            blocked_item = QTableWidgetItem(blocked_text)
            self.main_table.setItem(row, 3, blocked_item)
            self.main_table.setItem(row, 4, QTableWidgetItem(str(user['failed_attempts'])))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))

            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u))

            if user['is_blocked']:
                unblock_btn = QPushButton("🔓")
                unblock_btn.setFixedSize(30, 30)
                unblock_btn.clicked.connect(lambda checked, u=user: self.unblock_user(u))
                action_layout.addWidget(unblock_btn)

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            self.main_table.setCellWidget(row, 5, action_widget)

    def add_user(self):
        dialog = UserDialog(self.db)
        if dialog.exec_():
            self.load_users()

    def edit_user(self, user):
        dialog = UserDialog(self.db, user)
        if dialog.exec_():
            self.load_users()

    def delete_user(self, user):
        if user['login'] == self.current_user.login:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить самого себя!")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить пользователя '{user['login']}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_user(user['id_user'])
            self.load_users()

    def unblock_user(self, user):
        self.db.unblock_user(user['id_user'])
        self.load_users()
