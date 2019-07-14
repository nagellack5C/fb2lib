import sqlite3


def connect(create=None):
    '''
    Connects to database, creates new table if passed a create parameter
    :param create: if True, a new table is created
    :return: connection and cursor
    '''
    conn = sqlite3.connect("mydatabase.sqlite")
    cursor = conn.cursor()
    if create:
        # cursor.execute("""CREATE TABLE books
        #                    (title TEXT, first_name TEXT, middle_name TEXT, last_name TEXT,
        #                    nickname TEXT, year INT)
        #                """)

        cursor.execute("""CREATE TABLE books
                          (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          str_repr TEXT,
                           author TEXT, title TEXT, bookdate INT)
                       """)
        conn.commit()
    return conn, cursor


def get_reprs():
    '''
    Returns all string representations as a set to enable updating
    '''
    conn, cursor = connect()
    return set([i[0] for i in cursor.execute("SELECT str_repr FROM books")])


def adder(books_found):
    '''
    Writes found books to the database
    :param books_found: list/set of books parsed
    '''
    if isinstance(books_found, set):
        books_found = list(books_found)
    print(f"Добавляем {len(books_found)} записей... ", end="")
    conn, cursor = connect()
    cursor.executemany("INSERT INTO books(str_repr, author, title, bookdate)"
                       "VALUES (?,?,?,?)",
                       books_found)
    conn.commit()
    conn.close()
    print("готово!")


def seek_book(args):
    '''
    Constructs a query that selects books from the database according to the
    user-defined criteria.
    :param args: user-defined arguments
    :return: list of books that match the request
    '''
    conn, cursor = connect()
    new_args = []
    query = "SELECT * FROM books WHERE "
    q_vals = []
    for arg in ["author", "title", "bookdate"]:
        if args[arg]:
            q_vals.append(f"{arg} = ?")
            new_args.append(args[arg])
    new_args = tuple(new_args)
    query = query + " AND ".join(q_vals)
    cursor.execute(query, new_args)
    result = cursor.fetchall()
    if result:
        for i in result:
            print(f"{i[2]}: {i[3]}, {i[4] if i[4] else 'Дата неизвестна'},"
                  f"номер: {i[0]}")
    else:
        print("Нет результатов. Попробуйте другой запрос")


def deleter(args):
    '''
    Deletes one or all books from the database.
    :param args: user-defined arguments
    '''
    conn, cursor = connect()

    if args["number"]:
        cursor.execute("DELETE FROM books WHERE id = ?", (args["number"],))
    if args["wipe"]:
        cursor.execute("DELETE FROM books")
    conn.commit()


if __name__ == "__main__":
    connect(create=True)
