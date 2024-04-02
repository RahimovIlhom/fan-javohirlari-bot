import datetime
import sqlite3

from utils.db_api import post_or_put_data


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @property
    async def connect(self):
        return sqlite3.connect(self.db_path)

    async def select_users(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from users")
        return resp.fetchall()

    async def select_user(self, tg_id, *args, **kwargs):
        # (1282, '5442563505', 'uzbek', 'wevge', '+998336589340', 'Andijon viloyati', "Bo'z tumani",
        # '3', 'FIZIKA', '2024-02-19 20:37:57.876955', '2024-03-18 04:04:23.423830', '-', '-', '-', pinfl)
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"select * from users where tg_id={tg_id}")
        return resp.fetchone()

    async def select_user_phone(self, phone_number, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"select * from users where phone_number={phone_number}")
        return resp.fetchone()

    async def add_or_update_user(self, tg_id, language, fullname, phone, region, district, school, science, sc1='-',
                                 sc2='-', sc3='-', pinfl='-', *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        if await self.select_user(tg_id):
            SQL_query = ("update users set language=?, fullname=?, phone_number=?, region=?, district=?, "
                         "school_number=?, science_1=?, science_2=?, science_3=?, olimpia_science=?, update_time=?, "
                         "pinfl=? where tg_id=?;")
            cur.execute(SQL_query, (
                language, fullname, phone, region, district, school, sc1, sc2, sc3, science, datetime.datetime.now(),
                pinfl,
                tg_id))
        else:
            SQL_query = ("insert into users (tg_id, language, fullname, phone_number, region, district, school_number, "
                         "science_1, science_2, science_3, olimpia_science, created_time, update_time, pinfl) values "
                         "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);")
            cur.execute(SQL_query, (tg_id, language, fullname, phone, region, district, school, sc1, sc2, sc3, science,
                                    datetime.datetime.now(), datetime.datetime.now(), pinfl))
        conn.commit()
        user_data = await self.select_user(tg_id)
        await post_or_put_data(*user_data)

    async def update_pinfl(self, tg_id, pinfl):
        conn = await self.connect
        cur = conn.cursor()
        SQL_query = "update users set pinfl=? where tg_id=?;"
        cur.execute(SQL_query, (pinfl, tg_id))
        conn.commit()
        user_data = await self.select_user(tg_id)
        await post_or_put_data(*user_data)

    async def select_column_names(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from users")
        names = tuple(map(lambda x: x[0], resp.description))
        return names

    async def select_result_test_user(self, tg_id, science, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        test_id = cur.execute(f"SELECT * FROM tests WHERE science = ? and is_confirm = ? and olympiad_test = ?",
                              (science, True, olympiad_test)).fetchall()[-1][0]
        resp = cur.execute(f"SELECT * FROM test_result WHERE tg_id = ? and test_id = ?", (tg_id, test_id))
        return resp.fetchone()

    async def select_test(self, science, language=None, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        # ('id', 'science', 'create_time', 'language', 'questions_count', 'is_confirm',
        # 'end_time', 'olympiad_test', 'start_time')

        # (15, 'FIZIKA', '2024-03-02', 'uzbek', 4, 1, None, 1, None)
        if language is None:
            sql_query = f"SELECT * FROM tests WHERE science = ? and is_confirm = ? and olympiad_test=?"
            resp = cur.execute(sql_query, (science, True, olympiad_test)).fetchall()
        else:
            sql_query = f"SELECT * FROM tests WHERE science = ? and is_confirm = ? and language = ? and olympiad_test=?"
            resp = cur.execute(sql_query,
                               (science, True, language, olympiad_test)).fetchall()
        if resp:
            return resp[-1]
        return False

    async def select_tests(self, science, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT * FROM tests WHERE science = ? and is_confirm = ? and olympiad_test = ?",
                           (science, True, olympiad_test)).fetchall()
        if resp:
            return resp
        return False

    async def select_question(self, test_id, number):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("""
            SELECT * 
            FROM test_questions
            INNER JOIN test_questions_test
            ON test_questions.id = test_questions_test.testquestion_id
            WHERE test_questions_test.test_id = ? 
            AND test_questions.number_question = ?
            """, (test_id, number))
        return resp.fetchone()

    async def add_test_result(self, test_id, tg_id, language, fullname, phone_number, region, district, school_number,
                              science, responses, result_time, pinfl=None, certificate_image=None, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        sql_query = ("INSERT INTO test_result (tg_id, language, fullname, phone_number, region, district, "
                     "school_number, science, responses, result_time, test_id, pinfl, certificate_image) VALUES (?, "
                     "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);")
        cur.execute(sql_query, (
            tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time,
            test_id, pinfl, certificate_image))
        conn.commit()

    async def select_science_tests(self, science, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from tests where science = ? and olympiad_test = ?",
                           (science, olympiad_test)).fetchall()
        if resp:
            return resp[::-1]
        return False

    async def select_all_tests(self):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from tests").fetchall()
        if resp:
            return resp[::-1]
        return False

    async def select_questions_test_id(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("""
                    SELECT * 
                    FROM test_questions
                    INNER JOIN test_questions_test
                    ON test_questions.id = test_questions_test.testquestion_id
                    WHERE test_questions_test.test_id = ?
                    """, (test_id,))
        return resp.fetchall()

    async def add_test(self, science, language, count, end_time=None, olympiad=False, start_time=None, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("insert into tests (science, create_time, language, questions_count, is_confirm, "
                    "end_time, olympiad_test, start_time) values (?, ?, ?, ?, ?, ?, ?, ?);",
                    (science, datetime.datetime.now().date(), language, count, False, end_time, olympiad, start_time))
        conn.commit()

    async def select_test_id(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT * FROM tests WHERE id = ?", (test_id,))
        return resp.fetchone()

    async def delete_test(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"DELETE FROM tests WHERE id = ?", (test_id,))
        conn.commit()

    async def add_question_test(self, number_question, question_uz, question_ru, true_response, test_id, image_id=None,
                                *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()

        if int(kwargs.get('quantity')) <= number_question:
            cur.execute("update tests set is_confirm = ? where id = ?", (True, test_id))
            conn.commit()

        # TestQuestions jadvaliga yangi ma'lumotni qo'shish
        cur.execute(
            "INSERT INTO test_questions (number_question, question_uz, question_ru, true_response, image_id) VALUES ("
            "?, ?, ?, ?, ?);",
            (number_question, question_uz, question_ru, true_response, image_id)
        )

        # TestQuestions va Tests jadvallarini bog'lash
        cur.execute(
            "INSERT INTO test_questions_test (testquestion_id, test_id) VALUES (?, ?);",
            (cur.lastrowid, test_id)
        )

        conn.commit()

    async def update_question_test(self, question_id, question_uz, question_ru, true_response, image_id=None,
                                   *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("update test_questions set question_uz = ?, question_ru = ?, true_response = ?, image_id = ? "
                    "where id = ?",
                    (question_uz, question_ru, true_response, image_id, question_id))
        conn.commit()

    async def select_question_id(self, ques_id):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT * FROM test_questions WHERE id = ?", (ques_id,))
        return resp.fetchone()

    async def select_test_result_column_names(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select id, tg_id, language, fullname, pinfl, phone_number, region, district, "
                           "school_number, science, result_time from test_result")
        names = tuple(map(lambda x: x[0], resp.description))
        return names

    async def select_test_result(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT id, tg_id, language, fullname, pinfl, phone_number, region, district, "
                           f"school_number, science, result_time, responses FROM test_result WHERE test_id = ?",
                           (test_id,))
        return resp.fetchall()

    async def add_token(self, token):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("insert into tokens (token, created_time, active) values (?, ?, ?);",
                    (token, datetime.datetime.now(), True))
        conn.commit()
        cur.execute("update tokens set active=? where token!=?", (False, token))
        conn.commit()

    async def get_token(self):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from tokens where active=?;", (True, ))
        return resp.fetchone()

