import os

import sqlite3


def delete_test_result():
    db_file = os.path.abspath('db.sqlite3')
    connect = sqlite3.connect(db_file)
    cur = connect.cursor()
    sql_query = """
        DELETE FROM test_questions_test WHERE test_id NOT IN (SELECT id FROM tests);
    """
    cur.execute(sql_query)
    connect.commit()
    print("Error ignore")


delete_test_result()
