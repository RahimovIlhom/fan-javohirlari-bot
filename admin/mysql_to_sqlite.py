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


def users_mysql_to_sqlite():
    mycursor.execute("SELECT id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl FROM users")
    rows = mycursor.fetchall()

    SQL_SQLite = """
    INSERT INTO users (id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur_sqlite.executemany(SQL_SQLite, rows)

    conn_sqlite.commit()


def tokens_mysql_to_sqlite():
    mycursor.execute("SELECT id, token, created_time, active FROM tokens")
    rows = mycursor.fetchall()

    SQL_SQLite = """
    INSERT INTO tokens (id, token, created_time, active)
    VALUES (?, ?, ?, ?)
    """
    cur_sqlite.executemany(SQL_SQLite, rows)

    conn_sqlite.commit()


def tests_mysql_to_sqlite():
    mycursor.execute("SELECT id, science, create_time, language, questions_count, is_confirm, olympiad_test, start_time, end_time FROM tests")
    rows = mycursor.fetchall()

    SQL_SQLite = """
    INSERT INTO tests (id, science, create_time, language, questions_count, is_confirm, olympiad_test, start_time, end_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur_sqlite.executemany(SQL_SQLite, rows)

    conn_sqlite.commit()


def test_questions_mysql_to_sqlite():
    mycursor.execute("SELECT id, number_question, question_uz, question_ru, true_response, test_id, image_id FROM test_questions")
    rows = mycursor.fetchall()

    SQL_SQLite = """
    INSERT INTO test_questions (id, number_question, question_uz, question_ru, true_response, test_id, image_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cur_sqlite.executemany(SQL_SQLite, rows)

    conn_sqlite.commit()


def test_result_mysql_to_sqlite():
    mycursor.execute("SELECT id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id, pinfl, certificate_image FROM test_result")
    rows = mycursor.fetchall()

    SQL_SQLite = """
    INSERT INTO test_result (id, tg_id, language, fullname, phone_number, region, district, school_number, science, responses, result_time, test_id, pinfl, certificate_image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur_sqlite.executemany(SQL_SQLite, rows)

    conn_sqlite.commit()


if __name__ == '__main__':
    users_mysql_to_sqlite()
    tokens_mysql_to_sqlite()
    tests_mysql_to_sqlite()
    test_questions_mysql_to_sqlite()
    test_result_mysql_to_sqlite()
    conn_sqlite.close()
    mydb.close()
