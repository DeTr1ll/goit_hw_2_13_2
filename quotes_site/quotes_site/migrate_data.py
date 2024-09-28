import json
import psycopg2

# Путь к JSON файлам
authors_json_path = 'author.json'
quotes_json_path = 'quote.json'

# Установка соединения с базой данных
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="567234",
    host="127.0.0.1", 
    port="5432",
)
cursor = conn.cursor()

# Создание таблиц с обработкой ошибок
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotes_author (
        _id SERIAL PRIMARY KEY,
        fullname VARCHAR(255),
        born_date VARCHAR(255),
        born_location VARCHAR(255),
        description TEXT
    );
    """)
    print("Таблица 'quotes_author' создана или уже существует.")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotes_quote (
        _id SERIAL PRIMARY KEY,
        tags TEXT[],
        author INTEGER REFERENCES quotes_author(_id),
        quote TEXT
    );
    """)
    print("Таблица 'quote' создана или уже существует.")
except Exception as e:
    print("Ошибка при создании таблиц:", e)
    conn.rollback()
    cursor.close()
    conn.close()
    exit(1)

# Вставка авторов
try:
    with open(authors_json_path, 'r') as file:
        authors_data = json.load(file)

    for record in authors_data:
        try:
            # Проверка наличия необходимых полей
            fullname = record.get('fullname', None)
            born_date = record.get('born_date', None)
            born_location = record.get('born_location', None)
            description = record.get('description', None)

            # Если fullname отсутствует, пропускаем запись
            if fullname is None:
                print("Пропущена запись: отсутствует fullname")
                continue

            cursor.execute(
                """
                INSERT INTO quotes_author (fullname, born_date, born_location, description)
                VALUES (%s, %s, %s, %s)
                RETURNING _id
                """,
                (fullname, born_date, born_location, description)
            )
        except Exception as e:
            print("Ошибка при вставке данных автора:", e)
            conn.rollback()  # Отменяем транзакцию в случае ошибки
        else:
            author_id = cursor.fetchone()[0]
            print(f"Автор добавлен с ID: {author_id}")

except Exception as e:
    print("Ошибка при обработке авторов:", e)

# Вставка цитат

try:
    with open(quotes_json_path, 'r') as file:
        quotes_data = json.load(file)

    for record in quotes_data:
        try:
            # Извлечение OID автора
            author_oid = record['author']['$oid']

            # Поиск ID автора в таблице
            cursor.execute("SELECT _id FROM quotes_author WHERE _id::TEXT = %s", (author_oid,))
            author_id = cursor.fetchone()

            # Проверка, найден ли автор
            if author_id is None:
                print(f"Автор с OID {author_oid} не найден. Цитата пропущена.")
                continue

            # Вставка цитаты
            cursor.execute(
                """
                INSERT INTO quotes_quote (tags, author_id, quote)
                VALUES (%s, %s, %s)
                """,
                (record['tags'], author_id[0], record['quote'])
            )
        except Exception as e:
            print("Ошибка при вставке данных цитаты:", e)
            conn.rollback()  # Отменяем транзакцию в случае ошибки

except Exception as e:
    print("Ошибка при обработке цитат:", e)

# Коммит транзакции
try:
    conn.commit()
    print("Данные успешно вставлены.")
except Exception as e:
    print("Ошибка при коммите:", e)

# Закрытие соединения
cursor.close()
conn.close()