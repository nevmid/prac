import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                database="manufacturing",
                host="localhost",
                password="1234",
                user="postgres",
            )
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def get_user(self, login, password):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE login=%s AND password=%s",
                           (login, password))
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при получении пользователя: {e}")
            return None
        finally:
            self.close_connection()

    def get_user_by_login(self, login):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE login=%s",
                           (login,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при получении пользователя по логину: {e}")
            return None
        finally:
            self.close_connection()

    def update_failed_attempts(self, id, new_att):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute("UPDATE users SET failed_attempts=%s WHERE id_user=%s",
                           (new_att, id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении счётчика попыток: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close_connection()

    def block_user(self, id):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute("UPDATE users SET is_blocked = true, failed_attempts = 0 WHERE id_user=%s",
                           (id, ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка блокировки: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close_connection()

    def reset_failed_attempts(self, user_id):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET failed_attempts = 0 WHERE id_user = %s",
                (user_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка сброса попыток: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close_connection()

    def get_all_users(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users ORDER BY id_user")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения пользователей: {e}")
            return []
        finally:
            self.close_connection()

    def get_customers(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM customers")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения заказчиков: {e}")
            return []
        finally:
            self.close_connection()

    def get_orders(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT oi.id_order, oi.id_product, oi.count, oi.price_at_order,"
                           "o.order_date, o.order_number, o.id_customer "
                           "FROM order_items oi "
                           "JOIN orders o ON o.id_order = oi.id_order "
                           )
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения заказов: {e}")
            return []
        finally:
            self.close_connection()

    def get_specifications(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT si.id_specification, si.id_material, si.consumption_rate, "
                           "s.name, s.id_product "
                           "FROM specification_items si "
                           "JOIN specifications s ON s.id_specification = si.id_specification "
                           )
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения спецификаций: {e}")
            return []
        finally:
            self.close_connection()

    def get_products(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM products")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения продуктов: {e}")
            return []
        finally:
            self.close_connection()

    def get_materials(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM materials")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения материалов: {e}")
            return []
        finally:
            self.close_connection()

    def get_productions(self):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM productions")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения производств: {e}")
            return []
        finally:
            self.close_connection()

    def create_user(self, login, password, role='user'):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (login, password, role) VALUES (%s, %s, %s) RETURNING id_user",
                (login, password, role)
            )
            user_id = cursor.fetchone()[0]
            self.conn.commit()
            return user_id
        except Exception as e:
            print(f"Ошибка добавленияпользователя: {e}")
            return None
        finally:
            self.close_connection()

    def update_user(self, user_id, login, password, role, is_blocked):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET login = %s, password = %s, role = %s, is_blocked = %s WHERE id_user = %s",
                (login, password, role, is_blocked, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления пользователя: {e}")
            return False
        finally:
            self.close_connection()

    def delete_user(self, user_id):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users WHERE id_user = %s", (user_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления пользователя: {e}")
            return False
        finally:
            self.close_connection()

    def unblock_user(self, user_id):
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(
                    "UPDATE users SET is_blocked = false, failed_attempts = 0 WHERE id_user = %s",
                    (user_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка разблокировки: {e}")
        finally:
            self.close_connection()
