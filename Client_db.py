import psycopg2

def create_db(conn):
    # удаление таблиц
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS phones;
        DROP TABLE IF EXISTS clients;
        """)
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

# Функция, позволяющая добавить клиента в базу данных
def add_client(conn, first_name, last_name, e_mail, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
               SELECT id FROM clients
                   WHERE e_mail = %s
                   """, (e_mail,))
        name_match = cur.fetchone()
        cur.execute("""
               SELECT client_id FROM phones
                   WHERE phone = %s
                   """, (phone,))
        phone_match = cur.fetchone()
    if name_match and phone_match:
        print("Ошибка добавления клиента:")
        print("Клиент с Email: {}".format(e_mail), "уже существует, id:", name_match[0])
        print("Клиент с телефоном: {}".format(phone), "уже существует, id:", phone_match[0])
    elif name_match:
        print("Ошибка добавления клиента:")
        print("Клиент с Email: {}".format(e_mail), "уже существует, id:", name_match[0])
    elif phone_match:
        print("Ошибка добавления клиента:")
        print("Клиент с телефоном: {}".format(phone), "уже существует, id:", phone_match[0])
    else:
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

# функция, позволяющая добавлить телефон у существующего клиента
def add_client_phone(conn, clientid, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
           SELECT client_id FROM phones
               WHERE phone = %s
               """, (phone,))
        phone_match = cur.fetchone()
    if phone_match:
        print("Ошибка добавления телефона. Номер {}".format(phone), "уже принадлежит клиенту:", phone_match[0])
    else:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM clients
                """)
            f = cur.fetchall()
            f_list = [i[0] for i in f]
            if clientid in f_list:
                cur.execute("""
                    INSERT INTO phones(client_id, phone) 
                    VALUES(%s, %s)
                    """, (clientid, phone))
            else:
                print("Невозможно добавить телефон: клиент", clientid, "не существует")

# Функция, удаляющая все телефоны существующего клиента
def delete_phones(conn, clientid):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM clients
                """)
        ids = cur.fetchall()
        if (clientid,) in ids:
            cur.execute("""
                DELETE FROM phones WHERE client_id = %s;
                """, (clientid,))
        else:
            print("Ошибка удаления: клиент с id:", clientid, "не найден")

# Функция, позволяющая ввести с клавиатуры номер телефона в формате INTEGER
def get_phone():
    while True:
        try:
            num = input("Введите номер телефона (enter - не менять номер телефона): ")
            if num == "":
                print("Вы не ввели новый телефон клиента")
                break
            else:
                return int(num)
        except ValueError:
            print("Вы ввели не число. Повторите ввод")

# Функция, позволяющая изменить данные клиента вводом с клавиатуры
def change_client(conn, clientid):
    print("ВВЕДИТЕ НОВЫЕ ДАННЫЕ КЛИЕНТА {}:".format(clientid))
    first_name = input("Введите имя клиента (enter - не менять имя): ")
    if first_name == "":
        print("Вы не ввели новое имя клиента")
    else:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE clients SET first_name=%s WHERE id = %s;
                """, (first_name, clientid))
    last_name = input("Введите фамилию клиента (enter - не менять фамилию): ")
    if last_name == "":
        print("Вы не ввели новую фамилию клиента")
    else:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE clients SET last_name = %s WHERE id = %s;
                """, (last_name, clientid))
    e_mail = input("Введите email клиента (enter - не менять email): ")
    if e_mail == "":
        print("Вы не ввели новый email клиента")
    else:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE clients SET e_mail = %s WHERE id = %s;
                """, (e_mail, clientid))
    phone = get_phone()
    # если у клиента было несколько номеров телефона, то вместо первого записываем новый номер, остальные удаляем
    if phone:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM phones
                WHERE client_id = %s;
                """, (clientid,))
            fo = cur.fetchone()
            fa = cur.fetchall()
            cur.execute("""
                UPDATE phones SET phone = %s WHERE id = %s; 
                """, (phone, fo))
        for p_id in fa:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM phones WHERE id = %s; 
                    """, (p_id,))

# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, phone):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT client_id FROM phones
                WHERE phone = %s
                """, (phone,))
        c_id = cur.fetchall()
        if c_id:
            cur.execute("""
                DELETE FROM phones WHERE phone = %s;
                """, (phone,))
        else:
            print("Ошибка удаления телефона. Номер", phone, "не найден")

# Функция, позволяющая удалить существующего клиента
def delete_client(conn, clientid):
    # СНАЧАЛА УДАЛЯЕМ ВСЕ ТЕЛЕФОНЫ КЛИЕНТА!:
    delete_phones(conn, clientid)
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM clients WHERE id = %s;
            """, (clientid,))

# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, firstname=None, lastname=None, email=None, phone=None):
    print("Поиск:")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM clients
                WHERE first_name = %s AND last_name = %s AND e_mail = %s
                """, (firstname, lastname, email))
        c_id = cur.fetchall()
        if not c_id:
            cur.execute("""
                SELECT id FROM clients
                    WHERE first_name = %s AND last_name = %s
                    """, (firstname, lastname))
            c_id = cur.fetchall()
            if not c_id:
                cur.execute("""
                    SELECT id FROM clients
                        WHERE e_mail = %s
                        """, (email,))
                c_id = cur.fetchall()
                if not c_id:
                    cur.execute("""
                        SELECT id FROM clients
                            WHERE first_name = %s OR last_name = %s
                            """, (firstname, lastname))
                    c_id = cur.fetchall()
                    if not c_id:
                        cur.execute("""
                            SELECT client_id FROM phones
                                WHERE phone = %s
                                """, (phone,))
                        c_id = cur.fetchall()
        if c_id:
            id_list = [i[0] for i in c_id]
            for id_n in id_list:
                cur.execute("""
                    SELECT phone FROM phones
                        WHERE client_id = %s
                        """, (id_n,))
                c_phones = cur.fetchall()
                phones_list = [t[0] for t in c_phones]  # список всех телефонов клиента
                phones_str = (', '.join(map(str, phones_list)))  # строка с перечислением всех телефонов клиента
                cur.execute("""
                    SELECT first_name, last_name, e_mail FROM clients
                        WHERE id = %s
                        """, (id_n,))
                client = cur.fetchone()
                print("Клиент, Имя: {},".format(client[0]), "Фамилия: {},".format(client[1]), "Email: {},".format(client[2]),
                      "Телефон(ы): {},".format(phones_str), "id:", id_n)
        else:
            print("Клиент, Имя: {},".format(firstname), "Фамилия: {},".format(lastname), "Email: {},".format(email), "Телефон: {},".format(phone), "не найден")


with psycopg2.connect(database="clients_db", user="postgres", password="bazadannykh") as conn:
    if __name__ == "__main__":
        create_db(conn)
        add_client(conn, 'John', 'Johnson', 'johnsemail', 555444)
        add_client(conn, 'Peter', 'Peterson', 'petersemail', 123321)
        add_client(conn, 'Jim', 'Jeferson', 'jimsemail', 222000)
        add_client(conn, 'Mike', 'Myers', 'mikesmemail')
        add_client(conn, 'John', 'Johnson', None, 100002)
        add_client(conn, 'John', 'Johnson', 'bemail', 222222)
        add_client(conn, 'Mike', 'Porter', None, 111110)
        add_client(conn, 'John', 'Johnson', 'johnsemail', 555333)
        add_client(conn, 'John', 'Johnson', None, )
        add_client(conn, 'John', 'Johnson', None, )
        add_client_phone(conn, 1, 454545)
        add_client_phone(conn, 10, 999888)
        add_client_phone(conn, 1, 550000)
        add_client_phone(conn, 2, 666777)
        add_client_phone(conn, 3, 333111)
        add_client_phone(conn, 4, 123321)
        delete_phone(conn, 222000)
        delete_phone(conn, 5500000)
        find_client(conn, 'sdf', 'lkhgyu', 'lkgyuot', 333111)
        find_client(conn, 'Jim', 'Jeferson', 'jimsemail')
        find_client(conn, 'Mike', 'Myers', 'mikesemail')
        find_client(conn, 'Ivan')
        find_client(conn, 'Mike')
        find_client(conn, 'John', 'Johnson')
        find_client(conn, None, None, None, 666777)
        add_client(conn, 'Harry', None, 'mikesmemail')
        add_client(conn, 'Harry', None, 'harrysemail', 333111)
        add_client(conn, None, None, 'petersemail', 222222)
        find_client(conn, None, 'Johnson')
        delete_phones(conn, 25)
        find_client(conn, None, 'Johnson', 'johnsemail')
        delete_client(conn, 22)
        add_client_phone(conn, 2, 666333)
        change_client(conn, 1)
conn.close()