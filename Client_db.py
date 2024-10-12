import psycopg2


def create_db(conn1):
    # удаление таблиц
    with conn1.cursor() as cur:
        cur.execute("""
        DROP TABLE phones;
        DROP TABLE clients;
        """)
    # создание таблиц
    with conn1.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(60) NOT NULL,
            last_name VARCHAR(60) NOT NULL,
            e_mail VARCHAR(40)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            phone INTEGER
            client_id INTEGER REFERENCES clients(id)
        );
        """)
        conn1.commit()


def add_client(conn2, first_name, last_name, e_mail, phones=None):
    # наполнение таблиц
    with conn2.cursor() as cur:
        cur.execute("""
            INSERT INTO clients(first_name, last_name, e_mail) VALUES(%s, %s, %s,%s);
            """, (first_name, last_name, e_mail))
        conn2.commit()

        # cur.execute("""
        #    SELECT id FROM clients

        cur.execute("""
            INSERT INTO phones(phones, client_id) VALUES(%s, %s);
            """), (phones, clients(id))
        conn2.commit()
        # фиксируем в БД


with psycopg2.connect(database="clients_db", user="postgres", password="bazadannykh") as conn:
    create_db(conn)
    add_client(conn, 'John', 'Johnson', 'johnsemail', 555444)
    add_client(conn, 'Peter', 'Peterson', 'petersemail', 123321)

conn.close()
