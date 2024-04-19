import datetime
import mysql.connector

from environs import Env

from utils.db_api import post_or_put_data

env = Env()
env.read_env()


class Database:
    @property
    async def connect(self):
        mydb = mysql.connector.connect(
            host=env.str("DB_HOST"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASSWORD"),
            database=env.str("DB_NAME"),
        )

        return mydb

    async def select_users(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("select * from users")
        return cur.fetchall()

    async def select_user(self, tg_id, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE tg_id = %s", (str(tg_id),))
        resp = cur.fetchone()
        if resp:
            return resp
        else:
            return None

    async def select_user_phone(self, phone_number, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE phone_number='{str(phone_number)}';")
        return cur.fetchone()

    async def add_or_update_user(self, tg_id, language, fullname, phone, region, district, school, science, sc1='-',
                                 sc2='-', sc3='-', pinfl='-', *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        if await self.select_user(f'{tg_id}'):
            SQL_query = ("update users set language=%s, fullname=%s, phone_number=%s, region=%s, district=%s, "
                         "school_number=%s, science_1=%s, science_2=%s, science_3=%s, olimpia_science=%s, "
                         "update_time=%s, pinfl=%s where tg_id=%s;")
            cur.execute(SQL_query, (
                language, fullname, phone, region, district, school, sc1, sc2, sc3, science, datetime.datetime.now(),
                pinfl, str(tg_id)))
        else:
            sql_query = "SELECT MAX(id) FROM users;"
            cur.execute(sql_query)
            max_id = cur.fetchone()[0]
            new_id = (max_id if max_id else 0) + 1
            SQL_query = ("insert into users (id, tg_id, language, fullname, phone_number, region, district, school_number, "
                         "science_1, science_2, science_3, olimpia_science, created_time, update_time, pinfl) values "
                         "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
            cur.execute(SQL_query, (new_id, str(tg_id), language, fullname, phone, region, district, school, sc1, sc2, sc3, science,
                                    datetime.datetime.now(), datetime.datetime.now(), pinfl))
        conn.commit()
        user_data = await self.select_user(f'{tg_id}')
        await post_or_put_data(*user_data)

    async def update_pinfl(self, tg_id, pinfl):
        conn = await self.connect
        cur = conn.cursor()
        SQL_query = "update users set pinfl=%s where tg_id=%s;"
        cur.execute(SQL_query, (pinfl, str(tg_id)))
        conn.commit()
        user_data = await self.select_user(f'{tg_id}')
        await post_or_put_data(*user_data)

    async def select_column_names(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("select * from users")
        names = tuple(map(lambda x: x[0], cur.description))
        return names

    async def select_result_test_user(self, tg_id, science, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM tests WHERE science = %s and is_confirm = %s and olympiad_test = %s",
                    (science, True, olympiad_test))
        test_id = cur.fetchall()[-1][0]
        cur.execute(f"SELECT * FROM test_result WHERE tg_id = %s and test_id = %s", (f'{tg_id}', test_id))
        return cur.fetchone()

    async def select_test(self, science, language=None, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        if language is None:
            sql_query = f"SELECT * FROM tests WHERE science = %s and is_confirm = %s and olympiad_test=%s"
            cur.execute(sql_query, (science, True, olympiad_test))
        else:
            sql_query = f"SELECT * FROM tests WHERE science = %s and is_confirm = %s and language = %s and olympiad_test=%s"
            cur.execute(sql_query,
                        (science, True, language, olympiad_test))
        resp = cur.fetchall()
        if resp:
            return resp[-1]
        return False

    async def select_tests(self, science, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM tests WHERE science = %s and is_confirm = %s and olympiad_test = %s",
                    (science, True, olympiad_test))
        resp = cur.fetchall()
        if resp:
            return resp
        return False

    async def select_question(self, test_id, number):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("""
            SELECT * 
            FROM test_questions
            WHERE test_id = %s 
            AND number_question = %s
            """, (test_id, number))
        return cur.fetchone()

    async def add_test_result(self, test_id, tg_id, language, fullname, phone_number, region, district, school_number,
                              science, responses, result_time, pinfl=None, certificate_image=None, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        sql_query = "SELECT MAX(id) FROM test_result;"
        cur.execute(sql_query)
        max_id = cur.fetchone()[0]
        new_id = (max_id if max_id else 0) + 1
        sql_query = ("INSERT INTO test_result (id, tg_id, language, fullname, phone_number, region, district, "
                     "school_number, science, responses, result_time, test_id, pinfl, certificate_image) VALUES (%s, "
                     "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
        cur.execute(sql_query, (
            new_id, str(tg_id), language, fullname, phone_number, region, district, school_number, science, responses, result_time,
            test_id, pinfl, certificate_image))
        conn.commit()

    async def select_science_tests(self, science, olympiad_test=False):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("select * from tests where science = %s and olympiad_test = %s",
                    (science, olympiad_test))
        resp = cur.fetchall()
        if resp:
            return resp[::-1]
        return False

    async def select_all_tests(self):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("select * from tests")
        resp = cur.fetchall()
        if resp:
            return resp[::-1]
        return False

    async def select_questions_test_id(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("""
                    SELECT * 
                    FROM test_questions
                    WHERE test_id = %s
                    """, (test_id,))
        resp = cur.fetchall()
        return resp

    async def add_test(self, science, language, count, end_time=None, olympiad=False, start_time=None, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        sql_query = "SELECT MAX(id) FROM tests;"
        cur.execute(sql_query)
        max_id = cur.fetchone()[0]
        new_id = (max_id if max_id else 0) + 1
        cur.execute("insert into tests (id, science, create_time, language, questions_count, is_confirm, "
                    "end_time, olympiad_test, start_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (new_id, science, datetime.datetime.now().date(), language, count, False, end_time, olympiad, start_time))
        conn.commit()

    async def select_test_id(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM tests WHERE id = %s", (test_id,))
        return cur.fetchone()

    async def delete_test(self, test_id):
        conn = await self.connect
        cur = conn.cursor()

        cur.execute("DELETE FROM test_questions WHERE test_id = %s", (test_id,))
        cur.execute("DELETE FROM tests WHERE id = %s", (test_id,))
        conn.commit()

    async def add_question_test(self, number_question, question_uz, question_ru, true_response, test_id, image_id=None,
                                *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()

        if int(kwargs.get('quantity')) <= number_question:
            cur.execute("update tests set is_confirm = %s where id = %s", (True, test_id))
            conn.commit()

        sql_query = "SELECT MAX(id) FROM test_questions;"
        cur.execute(sql_query)
        max_id = cur.fetchone()[0]
        new_id = (max_id if max_id else 0) + 1

        # TestQuestions jadvaliga yangi ma'lumotni qo'shish
        cur.execute(
            "INSERT INTO test_questions (id, number_question, question_uz, question_ru, true_response, image_id, test_id) VALUES ("
            "%s, %s, %s, %s, %s, %s, %s);",
            (new_id, number_question, question_uz, question_ru, true_response, image_id, test_id)
        )

        conn.commit()

    async def update_question_test(self, question_id, question_uz, question_ru, true_response, image_id=None,
                                   *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("update test_questions set question_uz = %s, question_ru = %s, true_response = %s, image_id = %s "
                    "where id = %s",
                    (question_uz, question_ru, true_response, image_id, question_id))
        conn.commit()

    async def select_question_id(self, ques_id):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM test_questions WHERE id = %s", (ques_id,))
        return cur.fetchone()

    async def select_test_result_column_names(self, *args, **kwargs):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("select id, tg_id, language, fullname, pinfl, phone_number, region, district, "
                    "school_number, science, result_time from test_result")
        names = tuple(map(lambda x: x[0], cur.description))
        return names

    async def select_test_result(self, test_id):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute(f"SELECT id, tg_id, language, fullname, pinfl, phone_number, region, district, "
                    f"school_number, science, result_time, responses FROM test_result WHERE test_id = %s",
                    (test_id,))
        return cur.fetchall()

    async def add_token(self, token):
        conn = await self.connect
        cur = conn.cursor()
        sql_query = "SELECT MAX(id) FROM tokens;"
        cur.execute(sql_query)
        max_id = cur.fetchone()[0]
        new_id = (max_id if max_id else 0) + 1

        cur.execute("insert into tokens (id, token, created_time, active) values (%s, %s, %s, %s);",
                    (new_id, token, datetime.datetime.now(), True))
        conn.commit()
        cur.execute("update tokens set active=%s where token!=%s", (False, token))
        conn.commit()

    async def get_token(self):
        conn = await self.connect
        cur = conn.cursor()
        cur.execute("select * from tokens where active=%s;", (True,))
        return cur.fetchone()
