import sqlite3
import mysql.connector
from environs import Env

env = Env()
env.read_env()


mydb = mysql.connector.connect(
    host=env.str("DB_HOST"),
    user=env.str("DB_USER"),
    password=env.str("DB_PASSWORD"),
    database=env.str("DB_NAME"),
)

mycursor = mydb.cursor()

mydb.commit()

conn_sqlite = sqlite3.connect('db.sqlite3')
cur_sqlite = conn_sqlite.cursor()


def users_sqlite_to_mysql():
    cur_sqlite.execute("SELECT id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl FROM users")
    rows = cur_sqlite.fetchall()

    SQL_MySQL = """
    INSERT INTO users (id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    mycursor.executemany(SQL_MySQL, rows)

    mydb.commit()


def tokens_sqlite_to_mysql():
    cur_sqlite.execute("SELECT id, token, created_time, active FROM tokens")
    rows = cur_sqlite.fetchall()

    SQL_MySQL = """
    INSERT INTO tokens (id, token, created_time, active)
    VALUES (%s, %s, %s, %s)
    """
    mycursor.executemany(SQL_MySQL, rows)

    mydb.commit()


def tests_sqlite_to_mysql():
    cur_sqlite.execute("SELECT id, science, create_time, language, questions_count, is_confirm, olympiad_test, start_time, end_time FROM tests")
    rows = cur_sqlite.fetchall()

    SQL_MySQL = """
    INSERT INTO tests (id, science, create_time, language, questions_count, is_confirm, olympiad_test, start_time, end_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # row = list(row[:5]) + [bool(row[5]), bool(row[6])] + list(row[7:])
    mycursor.executemany(SQL_MySQL, rows)

    mydb.commit()


def test_questions_sqlite_to_mysql():
    resp = cur_sqlite.execute("SELECT id, number_question, question_uz, question_ru, true_response, test_id, image_id FROM test_questions")
    rows = resp.fetchall()

    SQL_MySQL = """
    INSERT INTO test_questions (id, number_question, question_uz, question_ru, true_response, test_id, image_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    # row = list(row[:5]) + [test_id] + [row[5]]
    mycursor.executemany(SQL_MySQL, rows)

    mydb.commit()


def test_result_sqlite_to_mysql():
    cur_sqlite.execute("SELECT id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id, pinfl, certificate_image FROM test_result")
    rows = cur_sqlite.fetchall()

    SQL_MySQL = """
    INSERT INTO test_result (id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id, pinfl, certificate_image)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    mycursor.executemany(SQL_MySQL, rows)

    mydb.commit()


if __name__ == '__main__':
    users_sqlite_to_mysql()
    tokens_sqlite_to_mysql()
    tests_sqlite_to_mysql()
    test_questions_sqlite_to_mysql()
    test_result_sqlite_to_mysql()
    conn_sqlite.close()
    mydb.close()
