import datetime
import sqlite3


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
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"select * from users where tg_id={tg_id}")
        return resp.fetchone()

    async def select_user_phone(self, phone_number, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"select * from users where phone_number={phone_number}")
        return resp.fetchone()

    async def add_or_update_user(self, tg_id, language, fullname, phone, region, district, school, science, sc1='-', sc2='-', sc3='-', *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        if await self.select_user(tg_id):
            SQL_query = ("update users set language=?, fullname=?, phone_number=?, region=?, district=?, "
                         "school_number=?, science_1=?, science_2=?, science_3=?, olimpia_science=?, update_time=? "
                         "where tg_id=?;")
            cur.execute(SQL_query, (language, fullname, phone, region, district, school, sc1, sc2, sc3, science, datetime.datetime.now(), tg_id))
        else:
            SQL_query = ("insert into users (tg_id, language, fullname, phone_number, region, district, school_number, "
                         "science_1, science_2, science_3, olimpia_science, created_time, update_time) values (?, ?, ?,"
                         "?, ?, ?, ?, ?, ?, ?, ?, ?, ?);")
            cur.execute(SQL_query, (tg_id, language, fullname, phone, region, district, school, sc1, sc2, sc3, science,
                                    datetime.datetime.now(), datetime.datetime.now()))
        conn.commit()

    async def select_column_names(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from users")
        names = tuple(map(lambda x: x[0], resp.description))
        return names

    async def select_result_test_user(self, tg_id, science):
        conn = await self.connect
        cur = conn.cursor()
        test_id = cur.execute(f"SELECT * FROM tests WHERE science = ? and is_confirm = ?", (science, True)).fetchall()[-1][0]
        resp = cur.execute(f"select * from test_result where tg_id = ? and test_id = ?", (tg_id, test_id))
        return resp.fetchone()

    async def select_test(self, science):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT * FROM tests WHERE science = ? and is_confirm = ?", (science, True)).fetchall()
        if resp:
            return resp[-1]
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

    async def add_test_result(self, test_id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        sql_query = ("INSERT INTO test_result (tg_id, language, fullname, phone_number, region, district, "
                     "school_number, science, responses, result_time, test_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                     "?);")
        cur.execute(sql_query, (tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id))
        conn.commit()

    async def select_science_tests(self, science):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute("select * from tests where science = ?", (science, )).fetchall()
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

    async def add_test(self, science, time_continue, count, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("insert into tests (science, create_time, time_continue, questions_count, is_confirm) "
                    "values (?, ?, ?, ?, ?);",
                    (science, datetime.datetime.now().date(), time_continue, count, False))
        conn.commit()

    async def select_test_id(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT * FROM tests WHERE id = ?", (test_id, ))
        return resp.fetchone()

    async def delete_test(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"DELETE FROM tests WHERE id = ?", (test_id,))
        conn.commit()

    async def add_question_test(self, number_question, question_uz, question_ru, true_response, test_id, *args,
                                **kwargs):
        conn = await self.connect
        cur = conn.cursor()

        if int(kwargs.get('quantity')) <= number_question:
            cur.execute("update tests set is_confirm = ? where id = ?", (True, test_id))
            conn.commit()

        # TestQuestions jadvaliga yangi ma'lumotni qo'shish
        cur.execute(
            "INSERT INTO test_questions (number_question, question_uz, question_ru, true_response) VALUES (?, ?, ?, ?);",
            (number_question, question_uz, question_ru, true_response)
        )

        # TestQuestions va Tests jadvallarini bog'lash
        cur.execute(
            "INSERT INTO test_questions_test (testquestion_id, test_id) VALUES (?, ?);",
            (cur.lastrowid, test_id)
        )

        conn.commit()

    async def update_question_test(self, question_id, question_uz, question_ru, true_response, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("update test_questions set question_uz = ?, question_ru = ?, true_response = ? where id = ?",
                    (question_uz, question_ru, true_response, question_id))
        conn.commit()

    async def select_question_id(self, ques_id):
        conn = await self.connect
        cur = conn.cursor()
        resp = cur.execute(f"SELECT * FROM test_questions WHERE id = ?", (ques_id,))
        return resp.fetchone()
