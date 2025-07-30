# 📚 SimpleDB

`SimpleDB`는 Python `sqlite3`를 기반으로 하는 간단한 SQLite 래퍼 클래스입니다.  
기본적인 테이블 생성, 데이터 삽입, 조회, 갱신, 삭제 등을 쉽게 할 수 있습니다.

---

## 주요 기능

- **SQLite 경량 데이터베이스 처리**
- **테이블 자동 생성**
- **간편한 CRUD 메서드**
- **조건 기반 SELECT/UPDATE/DELETE**
- **단일 컬럼 값 쉽게 찾기 (`find`)**

---

## 사용 예시

```python
from simpledb_wrapper.simpledb import SimpleDB

# 설치
# pip install simpledb-wrapper


# DB 인스턴스 생성 및 연결
db = SimpleDB("example.db")
db.connect()

# 테이블 생성
db.table("users", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "name": "TEXT",
    "age": "INTEGER"
})

# 데이터 삽입
db.insert("users", {"name": "Alice", "age": 25})

# 데이터 조회
results = db.select("users")
print(results)

# 조건부 조회
results = db.select("users", where="age > ?", where_params=(20,))
print(results)

# 데이터 수정
db.update("users", {"age": 30}, where="name = ?", where_params=("Alice",))

# 단일 값 찾기
age = db.find("users", "name", "Alice", "age")
print(f"Alice의 나이: {age}")

# 데이터 삭제
db.delete("users", where="name = ?", where_params=("Alice",))

# 연결 종료
db.close()
```

---

## 메서드 설명

### `connect()`
데이터베이스 파일에 연결합니다.

### `table(table_name, columns)`
테이블을 생성합니다.  
- `table_name`: 테이블 이름  
- `columns`: `{컬럼명: 타입}` 딕셔너리

### `insert(table, data)`
데이터를 삽입합니다.  
- `table`: 테이블 이름  
- `data`: `{컬럼명: 값}` 딕셔너리

### `select(...)`
데이터를 조회합니다.  
- `where`, `order_by`, `limit` 등 옵션 사용 가능

### `update(...)`
데이터를 수정합니다.

### `delete(...)`
데이터를 삭제합니다.

### `find(...)`
조건에 맞는 단일 값을 가져옵니다.

### `close()`
DB 연결을 종료합니다.
