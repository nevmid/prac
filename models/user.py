class User:
    def __init__(self, id_user, login, role, is_blocked):
        self.id = id_user
        self.login = login
        self.role = role
        self.is_blocked = is_blocked