import datetime
import logging
from uuid import uuid4

import aiomysql
from environs import Env
from utils.db_api import post_or_put_data

env = Env()
env.read_env()


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await aiomysql.create_pool(
                host=env.str("DB_HOST"),
                user=env.str("DB_USER"),
                password=env.str("DB_PASSWORD"),
                db=env.str("DB_NAME"),
                autocommit=True
            )

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute_query(self, query, *args, **kwargs):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                result = await cursor.fetchall()
        return result

    async def select_users(self, *args, **kwargs):
        query = "SELECT * FROM users"
        result = await self.execute_query(query)
        return result

    async def select_Tashkent_users(self, *args, **kwargs):
        query = "SELECT * FROM users WHERE region = %s"
        result = await self.execute_query(query, "Toshkent shahri")
        return result

    async def select_user(self, tg_id, *args, **kwargs):
        query = "SELECT * FROM users WHERE tg_id = %s"
        result = await self.execute_query(query, str(tg_id))
        return result[0] if result else None

    async def select_user_phone(self, phone_number, *args, **kwargs):
        query = f"SELECT * FROM users WHERE phone_number='{str(phone_number)}';"
        result = await self.execute_query(query)
        return result[0] if result else None

    async def add_or_update_user(self, tg_id, language, fullname, phone, region, district, school, science, sc1='-',
                                 sc2='-', sc3='-', pinfl='-', *args, **kwargs):
        existing_user = await self.select_user(str(tg_id))
        if existing_user:
            SQL_query = ("UPDATE users SET language=%s, fullname=%s, phone_number=%s, region=%s, district=%s, "
                         "school_number=%s, science_1=%s, science_2=%s, science_3=%s, olimpia_science=%s, "
                         "update_time=%s, pinfl=%s WHERE tg_id=%s;")
            await self.execute_query(SQL_query, language, fullname, str(phone), region, district, school, sc1, sc2, sc3,
                                     science, datetime.datetime.now(), pinfl, str(tg_id))
        else:
            sql_query = "SELECT MAX(id) FROM users;"
            max_id = (await self.execute_query(sql_query))[0][0]
            new_id = (max_id if max_id else 0) + 1
            SQL_query = ("INSERT INTO users (id, tg_id, language, fullname, phone_number, region, district, "
                         "school_number, science_1, science_2, science_3, olimpia_science, created_time, update_time, "
                         "pinfl) VALUES"
                         "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
            await self.execute_query(SQL_query, new_id, str(tg_id), language, fullname, str(phone), region, district,
                                     school, sc1, sc2, sc3, science,
                                     datetime.datetime.now(), datetime.datetime.now(), pinfl)
        user_data = await self.select_user(str(tg_id))
        await post_or_put_data(*user_data)

    async def update_pinfl(self, tg_id, pinfl):
        SQL_query = "UPDATE users SET pinfl=%s WHERE tg_id=%s;"
        await self.execute_query(SQL_query, *(pinfl, str(tg_id)))
        user_data = await self.select_user(str(tg_id))
        await post_or_put_data(*user_data)

    async def select_column_names(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("select * from users")
                names = tuple(map(lambda x: x[0], cursor.description))
                return names

    async def select_result_test_user(self, tg_id, science, olympiad_test=False):
        query = "SELECT * FROM tests WHERE science = %s AND is_confirm = %s AND olympiad_test = %s"
        tests = await self.execute_query(query, science, True, olympiad_test)
        test_id = tests[-1][0] if tests else None
        if test_id:
            query = "SELECT * FROM test_result WHERE tg_id = %s AND test_id = %s"
            resp = await self.execute_query(query, str(tg_id), test_id)
            if resp:
                return resp[-1]
            return None
        else:
            return None

    async def select_result_olympiad_user(self, tg_id):
        query_tests = """
            SELECT
                id, science, create_time, is_confirm, olympiad_test
            FROM tests
            WHERE is_confirm = %s AND olympiad_test = %s
            ORDER BY end_time;
        """
        all_tests = await self.execute_query(query_tests, True, True)
        tests = all_tests[7:]
        for ts in tests:
            query = ("SELECT id, tg_id, fullname, science, responses, interval_minute, "
                     "LENGTH(REPLACE(responses, '0', '')) AS correct_answers_count "
                     "FROM test_result "
                     "WHERE tg_id = %s AND test_id = %s")
            resp = await self.execute_query(query, str(tg_id), ts[0])
            if resp:
                return resp[0]
        return None

    async def select_result_active_olympiad_user(self, tg_id):
        query_tests = """
                SELECT
                    id, science, create_time, is_confirm, olympiad_test
                FROM tests
                WHERE is_confirm = %s AND olympiad_test = %s
                ORDER BY end_time;
            """
        all_tests = await self.execute_query(query_tests, True, True)
        tests = all_tests[7:]
        for ts in tests:
            query = ("SELECT id, tg_id, fullname, science FROM test_result "
                     "WHERE tg_id = %s AND test_id = %s")
            resp = await self.execute_query(query, str(tg_id), ts[0])
            if resp:
                return resp[0]
        return None

    async def select_result_for_science_new_olympiad(self, science):
        query_test = """
            SELECT id FROM tests
            WHERE is_confirm = %s AND olympiad_test = %s AND science = %s
            ORDER BY end_time;
        """
        science_tests = await self.execute_query(query_test, True, True, science)
        if len(science_tests) > 1:
            test = science_tests[-1]
            query = ("""
                SELECT id, tg_id, fullname, science, responses, interval_minute, 
                LENGTH(REPLACE(responses, '0', '')) AS correct_answers_count
                FROM test_result 
                WHERE test_id = %s
                ORDER BY correct_answers_count DESC, interval_minute ASC
            """)
            return await self.execute_query(query, test[0])
        return []

    async def select_all_result(self, test_id):
        query = ("""
            WITH ranked_results AS (
                SELECT 
                    tg_id, fullname, language, science, pinfl, phone_number, region, district, school_number, responses, 
                    interval_minute, result_time, LENGTH(REPLACE(responses, '0', '')) AS correct_answers_count,
                    ROW_NUMBER() OVER (ORDER BY LENGTH(REPLACE(responses, '0', '')) DESC, interval_minute ASC) AS number
                FROM test_result 
                WHERE test_id = %s
            )
            SELECT number, tg_id, fullname, language, science, pinfl, phone_number, region, district, school_number, 
            interval_minute, correct_answers_count, result_time, responses
            FROM ranked_results;
        """)
        return await self.execute_query(query, test_id)

    async def select_test(self, science, language=None, olympiad_test=False):
        if language is None:
            query = "SELECT * FROM tests WHERE science = %s AND is_confirm = %s AND olympiad_test=%s"
            resp = await self.execute_query(query, science, True, olympiad_test)
        else:
            query = "SELECT * FROM tests WHERE science = %s AND is_confirm = %s AND language = %s AND olympiad_test=%s"
            resp = await self.execute_query(query, science, True, language, olympiad_test)
        if olympiad_test and len(resp) > 1:
            return resp[-1]
        elif not olympiad_test and resp:
            return resp[-1]
        else:
            return False

    async def select_tests(self, science, olympiad_test=False):
        query = "SELECT * FROM tests WHERE science = %s AND is_confirm = %s AND olympiad_test = %s"
        return await self.execute_query(query, science, True, olympiad_test)

    async def select_question(self, test_id, number):
        query = "SELECT * FROM test_questions WHERE test_id = %s AND number_question = %s"
        return (await self.execute_query(query, test_id, number))[0]

    async def add_test_result(self, test_id, tg_id, language, fullname, phone_number, region, district, school_number,
                              science, responses, result_time, pinfl=None, certificate_image=None, olympiad_test=False,
                              interval_minute=None,  *args, **kwargs):
        test_result = await self.select_result_test_user(str(tg_id), science, olympiad_test)
        if test_result:
            query = ("UPDATE test_result SET language=%s, fullname=%s, phone_number=%s, region=%s, district=%s, "
                     "school_number=%s, science=%s, responses=%s, result_time=%s, pinfl=%s, certificate_image=%s, "
                     "interval_minute = %s WHERE test_id=%s AND tg_id=%s;")
            await self.execute_query(query, language, fullname, str(phone_number), region, district, school_number,
                                     science, responses, result_time, pinfl, certificate_image, interval_minute,
                                     test_id, str(tg_id))
        else:
            query = "SELECT MAX(id) FROM test_result;"
            max_id = (await self.execute_query(query))[0][0]
            new_id = (max_id if max_id else 0) + 1
            query = ("INSERT INTO test_result (id, tg_id, language, fullname, phone_number, region, district, "
                     "school_number, science, responses, result_time, test_id, pinfl, certificate_image, "
                     "interval_minute) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
            await self.execute_query(query, new_id, str(tg_id), language, fullname, str(phone_number), region,
                                     district, school_number, science, responses, result_time, test_id, pinfl,
                                     certificate_image, interval_minute)

    async def select_science_tests(self, science, olympiad_test=False):
        query = "SELECT * FROM tests WHERE science = %s AND olympiad_test = %s"
        return await self.execute_query(query, science, olympiad_test)

    async def select_all_tests(self):
        query = "SELECT * FROM tests"
        return await self.execute_query(query)

    async def select_questions_test_id(self, test_id):
        query = "SELECT * FROM test_questions WHERE test_id = %s"
        return await self.execute_query(query, test_id)

    async def add_test(self, science, language, count, end_time=None, olympiad=False, start_time=None, *args, **kwargs):
        query = "SELECT MAX(id) FROM tests;"
        max_id = (await self.execute_query(query))[0][0]
        new_id = (max_id if max_id else 0) + 1
        query = ("INSERT INTO tests (id, science, create_time, language, questions_count, is_confirm, "
                 "end_time, olympiad_test, start_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);")
        await self.execute_query(query, new_id, science, datetime.datetime.now().date(), language, count, False,
                                 end_time, olympiad, start_time)

    async def update_date_test(self, test_id, start_time, end_time):
        query = "UPDATE tests SET start_time = %s, end_time = %s WHERE id = %s"
        await self.execute_query(query, start_time, end_time, test_id)

    async def select_test_id(self, test_id):
        query = "SELECT * FROM tests WHERE id = %s"
        return (await self.execute_query(query, test_id))[0]

    async def delete_test(self, test_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM test_questions WHERE test_id = %s", (test_id,))
                await cur.execute("DELETE FROM tests WHERE id = %s", (test_id,))
                await conn.commit()

    async def add_question_test(self, number_question, question_uz, question_ru, true_response, test_id,
                                image_id=None, *args, **kwargs):
        query = "SELECT MAX(id) FROM test_questions;"
        max_id = (await self.execute_query(query))[0][0]
        new_id = (max_id if max_id else 0) + 1
        if int(kwargs.get('quantity', 0)) <= number_question:
            query = "UPDATE tests SET is_confirm = %s WHERE id = %s"
            await self.execute_query(query, True, test_id)
        query = ("INSERT INTO test_questions (id, number_question, question_uz, question_ru, true_response, image_id, "
                 "test_id) VALUES (%s, %s, %s, %s, %s, %s, %s);")
        await self.execute_query(query, new_id, number_question, question_uz, question_ru, true_response, image_id,
                                 test_id)

    async def update_question_test(self, question_id, question_uz, question_ru, true_response, image_id=None,
                                   *args, **kwargs):
        query = ("UPDATE test_questions SET question_uz = %s, question_ru = %s, true_response = %s, image_id = %s "
                 "WHERE id = %s")
        await self.execute_query(query, question_uz, question_ru, true_response, image_id, question_id)

    async def select_question_id(self, ques_id):
        query = "SELECT * FROM test_questions WHERE id = %s"
        return (await self.execute_query(query, ques_id))[0]

    async def select_test_result_column_names(self, *args, **kwargs):
        query = ("SELECT id, tg_id, language, fullname, pinfl, phone_number, region, district, school_number, "
                 "science, result_time FROM test_result")
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                if cursor.description:
                    names = tuple(map(lambda x: x[0], cursor.description))
                    return names
                else:
                    return None

    async def select_test_result(self, test_id):
        query = ("SELECT id, tg_id, language, fullname, pinfl, phone_number, region, district, school_number, "
                 "science, result_time, responses FROM test_result WHERE test_id = %s")
        return await self.execute_query(query, test_id)

    async def add_token(self, token):
        query = "SELECT MAX(id) FROM tokens;"
        max_id = (await self.execute_query(query))[0][0]
        new_id = (max_id if max_id else 0) + 1
        query = "INSERT INTO tokens (id, token, created_time, active) VALUES (%s, %s, %s, %s);"
        await self.execute_query(query, new_id, token, datetime.datetime.now(), True)
        query = "UPDATE tokens SET active = %s WHERE token != %s"
        await self.execute_query(query, False, token)

    async def get_token(self):
        query = "SELECT * FROM tokens WHERE active = %s"
        tokens = await self.execute_query(query, True)
        if tokens:
            return tokens[0]
        else:
            return None

    async def get_olympians_next_level(self, science):
        query = ("SELECT id, tg_id, fullname, phone_number, region, district, school_number, olympic_science, date, "
                 "time, created_time, pinfl, result, password, status FROM olympians WHERE olympic_science = %s")
        olympians = await self.execute_query(query, science)
        columns_names = ("id", "tg_id", "fullname", "phone_number", "region", "district", "school_number",
                         "olympic_science", "date", "time", "created_time", "pinfl", "result", "password", 'status')
        return columns_names, olympians

    async def select_result_user(self, tg_id, olympiad_test=True):
        query1 = "SELECT id FROM tests WHERE is_confirm = %s AND olympiad_test = %s"
        tests = await self.execute_query(query1, True, olympiad_test)
        if tests:
            tests_id = [test_app[0] for test_app in tests]
            placeholders = ','.join(['%s'] * len(tests_id))
            query2 = (f"SELECT id, tg_id, fullname, phone_number, region, district, school_number, science, responses, "
                      f"pinfl FROM test_result WHERE tg_id = %s AND test_id IN ({placeholders})")
            params = [str(tg_id)] + tests_id
            responses = await self.execute_query(query2, *params)
            resp = []
            if responses:
                for test_result in responses:
                    if test_result[8].count('1') / len(test_result[8]) > 0.66:
                        resp.append(test_result)
            return resp
        else:
            return []

    async def add_next_olympiad_user(self, tg_id, fullname, phone_number, region, district, school_number,
                                     olympic_science, result, pinfl, status):
        query1 = "SELECT * FROM olympians WHERE tg_id = %s"
        if status == 'comes':
            user_password = str(uuid4()).split('-')[0][:5]
            while await self.execute_query("select * from olympians where password = %s", user_password):
                user_password = str(uuid4()).split('-')[0][:5]
        else:
            user_password = None
        if await self.execute_query(query1, tg_id):
            query_update = ("UPDATE olympians SET fullname = %s, phone_number = %s, region = %s, district = %s, "
                            "school_number = %s, olympic_science = %s, result = %s, pinfl = %s, password = %s, "
                            "status = %s WHERE tg_id = %s")
            await self.execute_query(query_update, fullname, phone_number, region, district, school_number,
                                     olympic_science, result, pinfl, user_password, status, tg_id)
        else:
            query_add = ("INSERT INTO olympians (tg_id, fullname, phone_number, region, district, school_number, "
                         "olympic_science, result, pinfl, created_time, password, status) VALUES (%s, %s, %s, %s, %s, "
                         "%s, %s, %s, %s, %s, %s, %s);")
            await self.execute_query(query_add, tg_id, fullname, phone_number, region, district, school_number,
                                     olympic_science, result, pinfl, datetime.datetime.now(), user_password, status)

    async def get_next_olympiad_user(self, tg_id):
        query = "SELECT * FROM olympians WHERE tg_id = %s"
        return await self.execute_query(query, tg_id)

    async def get_next_olympiad_user_password(self, tg_id):
        query = "SELECT password FROM olympians WHERE tg_id = %s"
        return await self.execute_query(query, tg_id)

    async def select_next_level_users(self, olympiad_test=True):
        query1 = "SELECT id FROM tests WHERE is_confirm = %s AND olympiad_test = %s"
        tests = await self.execute_query(query1, True, olympiad_test)
        tests_id = [test_app[0] for test_app in tests]
        placeholders = ', '.join(['%s'] * len(tests_id))
        query2 = (f"SELECT DISTINCT tg_id "
                  f"FROM test_result "
                  f"WHERE test_id IN ({placeholders}) AND "
                  f"LENGTH(REPLACE(responses, '0', '')) / LENGTH(responses) > 0.66 "
                  f"AND tg_id NOT IN (SELECT tg_id FROM olympians);")

        return await self.execute_query(query2, *tests_id)
