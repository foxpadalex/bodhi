import sqlite3


class DataBase:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    # Работа с пользователями
    def user_exists(self, user_id):
        """Проверка по id"""
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    def user_exists_username(self, username):
        """Проверка юзера в базе по юзернейму (чтоб подтянуть данные)"""
        result = self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        return bool(len(result.fetchall()))

    def add_user_id(self, user_id, username):
        """Добавляем id пользователя из базы"""
        self.cursor.execute("UPDATE users SET user_id = ?, status = 1 WHERE username = ?", (user_id, username))
        self.conn.commit()

    def add_user(self, user_id, username, fn, ln, curator_id):
        """Добавляем нового пользователя"""
        self.cursor.execute("INSERT INTO users (user_id, username, first_name, last_name, curator_id, status) "
                            "VALUES (?, ?, ?, ?, ?, 1)",
                            (user_id, username, fn, ln, curator_id))
        self.conn.commit()

    def add_timezone(self, timezone, user_id):
        """Дополнить таймзону"""
        self.cursor.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (timezone, user_id))
        self.conn.commit()

    def get_users(self):
        """Получить всех юзеров"""
        result = self.cursor.execute("SELECT * FROM users WHERE status = 1")
        return result.fetchall()

    def get_users_curator(self, curator_id):
        """Получить всех пользователей куратора"""
        result = self.cursor.execute("SELECT * FROM users WHERE curator_id = ?", (curator_id,))
        return result.fetchall()

    def get_user(self, user_id):
        """Получить пользователя"""
        result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return result.fetchone()

    def get_user_id(self, username):
        result = self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        return result.fetchone()

    def add_username(self, username, fn, ln):
        """Добавляем пользователя в БД"""
        self.cursor.execute("INSERT INTO users (username, first_name, last_name) VALUES (?, ?, ?)", (username, fn, ln))
        self.conn.commit()

    def add_curator(self, username, curator_id):
        """Распределяем роли"""
        self.cursor.execute("UPDATE users SET curator_id = ? WHERE username = ?", (curator_id, username))
        self.conn.commit()

    # Работа с сообщениями, датами
    def get_msg(self, code):
        """Получить текст сообщения"""
        result = self.cursor.execute("SELECT text FROM msgs WHERE code = ?", (code,))
        return result.fetchone()[0]

    def add_sticker(self, code, file_id):
        self.cursor.execute("INSERT INTO stickers (file_id, code) VALUES (?, ?)", (file_id, code))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_sticker(self, code):
        result = self.cursor.execute("SELECT file_id FROM stickers WHERE code = ?", (code,))
        return result.fetchone()[0]

    def get_stickers(self, code):
        result = self.cursor.execute("SELECT file_id FROM stickers WHERE code = ?", (code,))
        return result.fetchall()

    def get_video(self, code):
        result = self.cursor.execute("SELECT link FROM video WHERE code = ?", (code,))
        return result.fetchone()[0]

    def add_video(self, code, link):
        """Меняем ссылку на видео (добавляем)"""
        self.cursor.execute("UPDATE video SET link = ? WHERE code = ?", (link, code))
        self.conn.commit()

    def add_before_photo(self, user_id, status, use_photo):
        """Можно ли использовать фото"""
        self.cursor.execute("INSERT INTO before_photos (user_id, status, use_photo) VALUES (?, ?, ?)",
                            (user_id, status, use_photo))
        self.conn.commit()

    def get_question(self, code):
        """Получить вопрос по анкете"""
        result = self.cursor.execute("SELECT question FROM training_questions WHERE code = ?", (code,))
        return result.fetchone()[0]

    def add_training_form(self, user_id, online, datetime):
        """Создаем анкету ответов"""
        self.cursor.execute("INSERT INTO history_training (user_id, online, datetime) VALUES (?, ?, ?)",
                            (user_id, online, datetime))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_form_id(self, user_id, datetime):
        """Получить id формы"""
        result = self.cursor.execute("SELECT id FROM history_training WHERE user_id = ? AND datetime = ?",
                                     (user_id, datetime))
        return result.fetchone()[0]

    def get_status_training_form(self, user_id, date):
        """Получить статус тренировки для ответа"""
        result = self.cursor.execute("SELECT online FROM history_training WHERE user_id = ? AND datetime = ?",
                                     (user_id, date))
        return result.fetchone()[0]

    def get_users_history(self, date):
        """Получить всех юзеров кто был сегодня"""
        result = self.cursor.execute("SELECT user_id FROM history_training WHERE datetime = ?", (date,))
        return result.fetchall()

    def add_answer_trainig(self, user_id, form_id, code, answer):
        """Добавить ответ"""
        self.cursor.execute("INSERT INTO answer_training (user_id, form_id, question_code, answer) VALUES (?, ?, ?, ?)",
                            (user_id, form_id, code, answer))
        self.conn.commit()

    def get_training_links(self, date):
        """Получить ссылку на тренировку"""
        result = self.cursor.execute("SELECT link FROM training_links WHERE datetime = ?", (date,))
        return result.fetchone()[0]

    def add_training_record(self, link, date):
        """Добавить ссылку на запись практики"""
        self.cursor.execute("INSERT INTO training_record (link, date) VALUES (?, ?)", (link, date))
        self.conn.commit()

    def get_training_records(self):
        """Получить все записи"""
        result = self.cursor.execute("SELECT * FROM training_record")
        return result.fetchall()

    def get_training_record(self, date):
        """Получить конкретную запись"""
        result = self.cursor.execute("SELECT * FROM training_record WHERE date = ?", (date,))
        return result.fetchone()

    def add_week_questions_form(self, user_id, date):
        """Недельная анкета"""
        self.cursor.execute("INSERT INTO week_questions (user_id, date) VALUES (?, ?)", (user_id, date))
        self.conn.commit()
        return self.cursor.lastrowid

    # def add_week_questions_answer(self, user_id, form_id, question_code, answer):
    #     """Добавить в БД ответ на недельную анкету"""
    #     self.cursor.execute("INSERT INTO week_questions_answer (user_id, form_id, question_code, answer) VALUES (?, ?, ?, ?)",
    #                         (user_id, form_id, question_code, answer))
    #     self.conn.commit()

    def add_week_answer(self, user_id, answer):
        """Добавить в БД ответ на недельную анкету"""
        self.cursor.execute("INSERT INTO week_answer (user_id, answer) VALUES (?, ?)", (user_id, answer))
        self.conn.commit()

    # Работа с админами
    def admin_exists(self, user_id):
        """Проверка админа в БД"""
        result = self.cursor.execute("SELECT id FROM admins WHERE user_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    def add_admin(self, user_id, username, first_name, last_name):
        """Добавить админа"""
        self.cursor.execute("INSERT INTO admins (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                            (user_id, username, first_name, last_name))
        self.conn.commit()

    def get_admin(self, user_id):
        """Получить админа"""
        result = self.cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
        return result.fetchone()

    def get_admins(self, status):
        """Получаем список админов"""
        if status is not None:
            result = self.cursor.execute("SELECT * FROM admins WHERE status = ?", (status,))
        else:
            result = self.cursor.execute("SELECT * FROM admins")
        return result.fetchall()

    def add_did_train(self, user_id, status, date):
        """Проверка был ли на тренировке"""
        self.cursor.execute("INSERT INTO did_train (user_id, status, date) VALUES (?, ?, ?)",
                            (user_id, status, date))
        self.conn.commit()

    def get_did_train(self):
        """Получить данные"""
        result = self.cursor.execute("SELECT did_train.user_id, users.username, did_train.status, did_train.date FROM did_train "
                                     "JOIN users ON users.user_id = did_train.user_id")
        return result.fetchall()

    # Переписка с саппортом
    def add_support_msg(self, user_id, curator_id, msg, status):
        """Сохранить переписку с саппортом"""
        self.cursor.execute("INSERT INTO to_support (user_id, curator_id, msg, status) VALUES (?, ?, ?, ?)",
                            (user_id, curator_id, msg, status))
        self.conn.commit()

    # def get_date(self, code):
    #     """Получаем дату по коду"""
    #     result = self.cursor.execute("SELECT datetime FROM date WHERE code = ?", (code,))
    #     return result.fetchone()[0]

    # Статистика
    def get_questions(self):
        """Получить список вопросов"""
        result = self.cursor.execute("SELECT * FROM training_questions")
        return result.fetchall()

    def get_user_statisctic(self, user_id):
        """Получить статистику по юзеру"""
        result = self.cursor.execute("SELECT history_training.datetime, training_questions.question, answer_training.answer "
                                     "FROM answer_training JOIN history_training ON history_training.id = answer_training.form_id "
                                     "JOIN training_questions ON training_questions.code = answer_training.question_code "
                                     "WHERE answer_training.user_id = ?", (user_id,))
        return result.fetchall()

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()
