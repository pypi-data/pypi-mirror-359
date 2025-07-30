import sqlite3

class SimpleDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def table(self, table_name, columns: dict):
        cols_defs = []
        for col_name, col_type in columns.items():
            cols_defs.append(f"{col_name} {col_type}")
        cols_str = ", ".join(cols_defs)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_str})"
        self.cursor.execute(sql)
        self.conn.commit()

    def insert(self, table, data: dict):
        keys = ', '.join(data.keys())
        question_marks = ', '.join(['?'] * len(data))
        values = tuple(data.values())

        sql = f"INSERT INTO {table} ({keys}) VALUES ({question_marks})"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def select(self, table, columns='*', where=None, where_params=(), order_by=None, limit=None):
        """
        - table: 테이블명
        - columns: '*' 또는 컬럼 리스트
        - where: WHERE 절 (예: "id = ? AND name = ?")
        - where_params: WHERE 절의 파라미터 튜플
        - order_by: 정렬 조건 (예: "id DESC")
        - limit: 결과 개수 제한 (정수)
        """
        if isinstance(columns, list):
            columns = ', '.join(columns)

        sql = f"SELECT {columns} FROM {table}"

        if where:
            sql += f" WHERE {where}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit:
            sql += f" LIMIT {limit}"

        self.cursor.execute(sql, where_params)
        return self.cursor.fetchall()

    def update(self, table, data: dict, where: str, where_params: tuple):
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = tuple(data.values()) + where_params

        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def delete(self, table, where: str, where_params: tuple):
        sql = f"DELETE FROM {table} WHERE {where}"
        self.cursor.execute(sql, where_params)
        self.conn.commit()

    def find(self, table, key_column, key_value, target_column):
        """
        - table: 테이블명
        - key_column: WHERE에 사용할 컬럼명
        - key_value: 찾을 값
        - target_column: 가져올 컬럼명
        """
        sql = f"SELECT {target_column} FROM {table} WHERE {key_column} = ?"
        self.cursor.execute(sql, (key_value,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"{key_column} {key_value} not found in table '{table}'")

    def close(self):
        if self.conn:
            self.conn.close()
