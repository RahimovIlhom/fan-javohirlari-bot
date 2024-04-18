import psycopg2
import sqlite3
from environs import Env

env = Env()
env.read_env()

conn_sqlite = sqlite3.connect('db.sqlite3')
cur_sqlite = conn_sqlite.cursor()

conn_postgres = psycopg2.connect(database=env.str("DB_NAME"),
                                 host=env.str("DB_HOST"),
                                 user=env.str("DB_USER"),
                                 password=env.str("DB_PASSWORD"),
                                 port=env.str("DB_PORT"))
cur_postgres = conn_postgres.cursor()


def users_sqlite_to_postgres():
    cur_sqlite.execute("SELECT id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl FROM users")
    rows = cur_sqlite.fetchall()

    for row in rows:
        SQL_POSTGRES = """
        INSERT INTO users (id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        if len(row[3]) < 255:
            cur_postgres.execute(SQL_POSTGRES, row)

    conn_postgres.commit()


def tokens_sqlite_to_postgres():
    cur_sqlite.execute("SELECT id, token, created_time, active FROM tokens")
    rows = cur_sqlite.fetchall()

    for row in rows:
        SQL_POSTGRES = """
        INSERT INTO tokens (id, token, created_time, active)
        VALUES (%s, %s, %s, %s)
        """
        row = list(row[:3]) + [bool(row[3])]
        cur_postgres.execute(SQL_POSTGRES, row)

    conn_postgres.commit()


def tests_sqlite_to_postgres():
    cur_sqlite.execute("SELECT id, science, create_time, language, questions_count, is_confirm, olympiad_test, start_time, end_time FROM tests")
    rows = cur_sqlite.fetchall()

    for row in rows:
        SQL_POSTGRES = """
        INSERT INTO tests (id, science, create_time, language, questions_count, is_confirm, olympiad_test, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        row = list(row[:5]) + [bool(row[5]), bool(row[6])] + list(row[7:])
        cur_postgres.execute(SQL_POSTGRES, row)

    conn_postgres.commit()


def test_questions_sqlite_to_postgres():
    resp = cur_sqlite.execute("SELECT id, number_question, question_uz, question_ru, true_response, image_id FROM test_questions")
    rows = resp.fetchall()

    for row in rows:
        test = cur_sqlite.execute("SELECT test_id FROM test_questions_test WHERE testquestion_id=?;", (row[0], ))
        test_id = test.fetchone()
        if test_id:
            test_id = test_id[0]
            SQL_POSTGRES = """
            INSERT INTO test_questions (id, number_question, question_uz, question_ru, true_response, test_id, image_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            row = list(row[:5]) + [test_id] + [row[5]]
            cur_postgres.execute(SQL_POSTGRES, row)

    conn_postgres.commit()


def test_result_sqlite_to_postgres():
    cur_sqlite.execute("SELECT id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id, pinfl, certificate_image FROM test_result")
    rows = cur_sqlite.fetchall()

    for row in rows:
        SQL_POSTGRES = """
        INSERT INTO test_result (id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id, pinfl, certificate_image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur_postgres.execute(SQL_POSTGRES, row)

    conn_postgres.commit()


if __name__ == '__main__':
    users_sqlite_to_postgres()
    tokens_sqlite_to_postgres()
    tests_sqlite_to_postgres()
    test_questions_sqlite_to_postgres()
    test_result_sqlite_to_postgres()
    conn_sqlite.close()
    conn_postgres.close()
