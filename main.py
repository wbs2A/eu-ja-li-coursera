import sqlite3
import os


def cls():
    os.system('cls||clear')


def get_book(user_info):
    book_name = input('insira o nome do livro a pesquisar:\n'
                      '> ')
    con = sqlite3.connect('eujali.db')
    cur = con.cursor()
    try:
        query = f"select name from book where name like '{book_name}%';"
        cur.execute(query)
        results = cur.fetchall()
        for book in results:
            print(book[0])
    except Exception as e:
        print(e)


def register_book_manually(user_info):
    book_name = input('nome do livro: ')
    page_quant = input('quantidade de páginas: ')
    ISBN = input('ISBN (opcional): ')
    genre = input('Gênero literário: ')

    con = sqlite3.connect('eujali.db')
    cur = con.cursor()

    query = f"select reader_id, points from reader where username = '{user_info['user']}' and password = '{user_info['pswd']}';"
    cur.execute(query)
    results = cur.fetchone()

    user_id, points = results[0], results[1]

    try:
        # register the book
        cur.execute(
            f"insert into book (name, page_quant, ISBN, genre) VALUES ('{book_name}', '{page_quant}', '{ISBN}', '{genre}');")
        con.commit()
        # assign to the user
        cur.execute(
            f"insert into reader_book (reader_id, book_id) values ({user_id}, {cur.lastrowid})"
        )
        con.commit()

        print('Livro registrado')

        current_book_points = (int(page_quant) // 100) + 1
        cur.execute(
            f"update reader set points = {int(points) + current_book_points} where reader_id = {user_id};"
        )
        con.commit()

        print('Pontuação atualizada')
    except Exception as e:
        print('livro não registrado, motivo: ', e)
    con.close()


def get_user_books(user_info):
    con = sqlite3.connect('eujali.db')
    cur = con.cursor()

    try:
        query = f"select reader_id from reader where username = '{user_info['user']}' and password = '{user_info['pswd']}';"
        cur.execute(query)
        user_id = cur.fetchone()[0]

        query = f"select book_id from reader_book where reader_id = {user_id};"
        cur.execute(query)
        books_from_user = cur.fetchall()

        for book in books_from_user:
            query = f"select name from book where book_id = {book[0]};"
            cur.execute(query)
            print(cur.fetchone()[0])
    except Exception as e:
        print(e)


def get_users_ranking(user_info):
    con = sqlite3.connect('eujali.db')
    cur = con.cursor()
    try:

        query = f"select name, points from reader where order by points DESC;"
        cur.execute(query)
        results = cur.fetchall()
        for reader_results in results:
            print(f"{reader_results[0]}\n\t pontos: {reader_results[1]}")
    except Exception as e:
        print(e)


def get_points_and_trophys(user_info):
    con = sqlite3.connect('eujali.db')
    cur = con.cursor()
    try:
        query = f"select reader_id, name, points from reader where username = '{user_info['user']}' and password = '{user_info['pswd']}';"
        cur.execute(query)
        user = cur.fetchone()
        print(f"{user[1]}\n\tpontos: {user[2]}")

        cur.execute(
            f"select book_id from reader_book where reader_id = {user[0]}"
        )
        books_user = cur.fetchall()
        books_ids = [x[0] for x in books_user]
        cur.execute(
            f"select genre, count(*) from book where book_id in {tuple(books_ids)} group by genre"
        )
        results = cur.fetchall()

        has_prize_flag = 0
        for row in results:
            if row[1] >= 5:
                has_prize_flag = 1
                print('\tLeitor de', row[0])
        if not has_prize_flag:
            print('\tAinda não conquistou nenhum prêmio')
    except Exception as e:
        print(e)


def create_user():
    print('---------- Vamos ao seu cadastro ----------')
    name = input("Seu nome:\n"
                 "> ")
    username = input('Seu login de acesso: \n'
                     '> ')
    password = input('Sua senha: \n'
                     '> ')
    con = sqlite3.connect('eujali.db')
    cur = con.cursor()
    try:
        cur.execute(
            f"insert into reader (username, name, password, points) VALUES ('{username}', '{name}', '{password}', 0);")
        con.commit()
    except Exception as e:
        print(e)
        return {}
    con.close()
    return {'user': username, 'pswd': password}


def login():
    print('---------- Você deve realizar o acesso ----------')
    username = input('login: ')
    password = input('senha: ')
    return {'user': username, 'pswd': password}


def check_login(user_info):
    try:
        con = sqlite3.connect("eujali.db")
        cur = con.cursor()
        statement = f"SELECT * from reader WHERE username='{user_info['user']}' AND Password = '{user_info['pswd']}';"
        cur.execute(statement)
        if not cur.fetchone():  # An empty result evaluates to False.
            print("Login não realizado")
            return False
        else:
            print(f"Olá, {user_info['user']}!")
        return True
    except KeyError as e:
        return False


def logout(user_info):
    return {}


def exit_the_system(user_info):
    exit(0)


def menu():
    return input("""
    1 - Visualizar lista de livros

    2 - Visualizar livro
    
    3 - Marcar leitura de livro manualmente

    4 - Visualizar ranking de usuários

    5 - Visualizar pontos e troféus de usuário
    
    9 - Fazer logout
    
    0 - Sair do sistema
    > 
    """)


def configurations():
    con = sqlite3.connect('eujali.db')
    cur = con.cursor()
    try:
        # Create the tables
        cur.execute('''
                   CREATE TABLE reader (
                        reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE, 
                        name TEXT,
                        password TEXT,
                        points INTEGER NULLABLE
                    );
                   ''')

        cur.execute('''
                   CREATE TABLE book (
                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        page_quant INTEGER,
                        ISBN TEXT NULLABLE,
                        genre TEXT NULLABLE
                    );
                   ''')

        cur.execute('''
                   CREATE TABLE reader_book (
                        reader_book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        reader_id INTEGER, 
                        book_id INTEGER,
                        FOREIGN KEY(reader_id) REFERENCES reader(reader_id),
                        FOREIGN KEY(book_id) REFERENCES book(book_id)
                    );
                   ''')

        # Insert the data
        cur.execute("INSERT INTO reader VALUES (1, 'admin', 'Super cleito', 'admini123', 0)")
        cur.execute("INSERT INTO book   VALUES (1, 'Fantastic Mr. Fox', 96, '9780140328721', 1, 'Historia infantil')")
        cur.execute("INSERT INTO reader_book VALUES (1, 1,1)")

        # Save (commit) the changes
        con.commit()
    except sqlite3.OperationalError as e:
        pass
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    configurations()
    users_info = {}

    menu_options = {
        '1': get_user_books,
        '2': get_book,
        '3': register_book_manually,
        '4': get_users_ranking,
        '5': get_points_and_trophys,
        '0': exit_the_system,
        '9': logout
    }
    while True:
        is_logged = check_login(users_info)
        if is_logged:
            choice = menu()
            try:
                if choice == '9':
                    users_info = menu_options[choice](users_info)
                menu_options[choice](users_info)
            except KeyError as e:
                cls()
                print('selecione uma opção válida, por favor.')
        else:
            cls()
            choice = input("Você deseja:\n"
                           "1 - Cadastrar\n"
                           "2 - Fazer login\n"
                           "> ")
            if choice == '1':
                users_info = create_user()
            elif choice == '2':
                users_info = login()
