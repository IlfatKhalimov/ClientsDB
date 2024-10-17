import psycopg2

def create_db(conn):
    # удаление таблиц
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS phones;
        DROP TABLE IF EXISTS clients;
        """)
    conn.commit()
    # создание таблиц
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(60) NOT NULL,
            last_name VARCHAR(60) NOT NULL,
            e_mail VARCHAR(40) UNIQUE
        );
        """)
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            phone INTEGER UNIQUE,
            client_id INTEGER REFERENCES clients(id)
        );
        """)
    conn.commit()

def add_client(conn, first_name, last_name, e_mail, phone=None):
    # наполнение таблиц
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients(first_name, last_name, e_mail) 
            VALUES(%s, %s, %s)
            RETURNING id;
            """, (first_name, last_name, e_mail))
        cur.execute("""
            INSERT INTO phones(phone, client_id) 
            VALUES(%s, %s)
            """, (phone, cur.fetchone()))
        conn.commit()
        # фиксируем в БД

# функция добавление телефона клиента
def add_client_phone(conn, firstname, lastname, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM clients
            WHERE first_name = %s AND last_name = %s
            """, (firstname, lastname))
        f = cur.fetchone()
        if f:
            cur.execute("""
                INSERT INTO phones(phone, client_id) 
                VALUES(%s, %s)
                """, (phone, f))
        else:
            print("Клиент", firstname, lastname, "не существует")
        conn.commit()

# Функция, удаляющая все телефоны существующего клиента
def delete_phones(conn, clientid):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones WHERE client_id=%s;
            """, (clientid,))
    conn.commit()

# функция, позволяющая изменить данные о клиенте
def change_client(conn, clientid, first_name=None, last_name=None, e_mail=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE clients SET first_name=%s, last_name=%s, e_mail=%s WHERE id=%s;
            """, (first_name, last_name, e_mail, clientid))
    conn.commit()
    # удаляем все телефоны клиента, т.к. телефонов может быть несколько
    delete_phones(conn, clientid)
    # записываем новый телефон клиента
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phones(phone, client_id) 
            VALUES(%s, %s)
            """, (phone, clientid))
    conn.commit()

# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones WHERE phone=%s;
            """, (phone,))
    conn.commit()

# Функция, позволяющая удалить существующего клиента
def delete_client(conn, clientid):
    # удаляем все телефоны удаляемого клиента
    delete_phones(conn, clientid)
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM clients WHERE id=%s;
            """, (clientid,))
    conn.commit()

# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, firstname=None, lastname=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id FROM clients c
                JOIN phones ph ON c.id = ph.client_id
                WHERE c.first_name = %s AND c.last_name = %s AND c.e_mail = %s OR ph.phone = %s
                """, (firstname, lastname, email, phone))
        c_id = cur.fetchone()
        if c_id:
            print("Клиент, Имя: {},".format(firstname), "Фамилия: {},".format(lastname), "Email: {},".format(email), "Телефон: {},".format(phone), "id:", c_id[0])
        else:
            print("Клиент, Имя: {},".format(firstname), "Фамилия: {},".format(lastname), "Email: {},".format(email), "Телефон: {},".format(phone), "не найден")
    conn.commit()


with psycopg2.connect(database="clients_db", user="postgres", password="bazadannykh") as conn:
    create_db(conn)
    add_client(conn, 'John', 'Johnson', 'johnsemail', 555444)
    add_client(conn, 'Peter', 'Peterson', 'petersemail', 123321)
    add_client(conn, 'Jim', 'Jeferson', 'jimsemail', 222000)
    add_client(conn, 'Mike', 'Myers', 'mikesemail', )
    add_client_phone(conn, 'John', 'Johnson', 454545)
    add_client_phone(conn, 'Jack', 'Johnson', 999888)
    add_client_phone(conn, 'John', 'Johnson', 550000)
    add_client_phone(conn, 'Peter', 'Peterson', 666777)
    add_client_phone(conn, 'Jim', 'Jeferson', 333111)
    # delete_phone(conn, 222000)
    change_client(conn, 1, 'Ron', 'Philips', 'ronsemail', 111000)
    delete_client(conn, 2)
    find_client(conn, 'sdf', 'lkhgyu', 'lkgyuot', 333111)
    find_client(conn, 'Jim', 'Jeferson', 'jimsemail')
    find_client(conn, 'Mike', 'Myers', 'mikesemail')
    find_client(conn, 'Ivan')
conn.close()