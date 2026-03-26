from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QDialog, QFormLayout, QLineEdit, QComboBox,
                             QMessageBox, QHeaderView, QCheckBox, QFocusFrame, QFrame)
from PyQt5.QtCore import Qt


class UserWindow(QMainWindow):
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
        frame_layout = QHBoxLayout(main_frame)
        btns_frame = QFrame()
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
        table_layout = QVBoxLayout(table_frame)

        self.main_table = QTableWidget()
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table_layout.addWidget(self.main_table)
        btns_layout.setAlignment(Qt.AlignTop)
        frame_layout.addWidget(btns_frame)
        frame_layout.addWidget(table_frame)
        main_layout.addWidget(main_frame)

    def load_customers(self):
        self.main_table.clear()
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
        users = self.db.get_all_users()
        self.main_table.setColumnCount(6)
        self.main_table.setHorizontalHeaderLabels(
            ["ID", "Логин", "Роль", "Заблокирован", "Попытки"])
        self.main_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(user['id_user'])))
            self.main_table.setItem(row, 1, QTableWidgetItem(user['login']))
            self.main_table.setItem(row, 2, QTableWidgetItem(user['role']))
            blocked_text = "Да" if user['is_blocked'] else "Нет"
            blocked_item = QTableWidgetItem(blocked_text)
            self.main_table.setItem(row, 3, blocked_item)
            self.main_table.setItem(row, 4, QTableWidgetItem(str(user['failed_attempts'])))
