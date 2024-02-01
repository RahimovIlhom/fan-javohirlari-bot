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
