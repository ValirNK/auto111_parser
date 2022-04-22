import pymysql.cursors

class DB_api:
    def __init__(self, host, db_name, db_user, db_pass):
        self.host = host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.cursor = False

    def connect(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.db_user,
            password=self.db_pass,
            db=self.db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        if connection:
            print('Подключились к базе данных')
            self.cursor = connection.cursor()
            return self.cursor
        else:
            print('Ошибка подключения к БД')
            return self.cursor

    def get_needs_8(self):
        if self.cursor != False:
            with self.cursor as cursor:
                sql = "SELECT * FROM needs_8 WHERE status = 1"
                cursor.execute(sql)
                for row in cursor:
                    id = str(row['id'])
                    part_sought = str(row['part_sought'])
                    brand_sought = str(row['brand_sought'])
                    id_1c_part = str(row['id_1c_part'])
                    id_1c_doc = str(row['id_1c_doc'])
                    status = str(row['status'])
                    yield {'id': id, 'part_sought': part_sought, 'brand_sought': brand_sought,
                           'id_1c_part': id_1c_part, 'id_1c_doc': id_1c_doc, 'status': status}

    def get_count_unparsed(self):
        if self.cursor != False:
            with self.cursor as cursor:
                sql = "SELECT COUNT(*) as count_unparsed FROM needs_8 WHERE status = 1"
                cursor.execute(sql)
                return cursor.fetchone()['count_unparsed']

    def get_count_parsed(self):
        if self.cursor != False:
            with self.cursor as cursor:
                sql = "SELECT COUNT(*) as count_parsed FROM needs_8 WHERE status = 0"
                cursor.execute(sql)
                return cursor.fetchone()['count_parsed']

db_obj = DB_api('localhost', 'autodoc', 'parser', 'jBDIbci39Aicu#')
connect = db_obj.connect()
if connect != False:
    print(db_obj.get_count_unparsed())
    # for i in db_obj.get_needs_8():
    #     print(i)
