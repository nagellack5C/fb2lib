import sqlite3


def connect():
    '''
    Connects to database, creates new table if passed a create parameter
    :param create: if True, a new table is created
    :return: connection and cursor
    '''
    conn = sqlite3.connect("mydatabase.sqlite")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS books
                      (str_repr TEXT PRIMARY KEY,
                       author TEXT, title TEXT, bookdate INT)
                   """)
    cursor.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS searchable_books
    USING FTS5(id, str_repr)
    """)
    conn.commit()
    return conn, cursor


def adder(books_found, update):
    '''
    Writes found books to the database
    :param books_found: list/set of books parsed
    '''
    print(f"Пишем {len(books_found)} книг в бд... ", end="")
    conn, cursor = connect()
    if update:
        cursor.executemany("INSERT OR REPLACE INTO"
                           "books(str_repr, author, title, bookdate)"
                           "VALUES (?,?,?,?)",
                           books_found)
    else:
        cursor.executemany("INSERT OR IGNORE INTO"
                           "books(str_repr, author, title, bookdate)"
                           "VALUES (?,?,?,?)",
                           books_found)
    conn.commit()
    conn.close()
    print("готово!")


def search_copy():
    print("Индексируем информацию о книгах... ", end="")
    cursor, conn = connect()
    cursor.execute("DELETE FROM searchable_books")
    cursor.execute("INSERT INTO searchable_books(id, str_repr)"
                   "SELECT rowid, str_repr FROM books ")
    cursor.commit()
    conn.close()
    print("Готово!")


def seek_book(args):
    conn, cursor = connect()
    new_args = []
    query = "SELECT rowid, * FROM books WHERE "
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
            print(f"{i[2]}: {i[3]}, {i[4] if i[4] else 'дата неизвестна'}, "
                  f"номер: {i[0]}")
    else:
        print("Нет результатов. Попробуйте другой запрос")


def fts_book(args):
    args = " ".join([args[i] for i in ["author", "title", "bookdate"]
                     if args[i]])
    if not args:
        return
    conn, cursor = connect()
    result = cursor.execute("SELECT rowid, * FROM books"
                            " WHERE rowid IN "
                            " (SELECT id FROM searchable_books"
                            " WHERE str_repr MATCH ?)", (args,)).fetchall()
    if result:
        print("\nВозможно, вам подойдут эти книги:")
        for i in result:
            print(f"{i[2]}: {i[3]}, {i[4] if i[4] else 'дата неизвестна'}, "
                  f"номер: {i[0]}")


def deleter(args):
    '''
    Deletes one or all books from the database.
    :param args: user-defined arguments
    '''
    conn, cursor = connect()

    if args["number"]:
        cursor.execute("DELETE FROM books WHERE rowid = ?",
                       (args["number"],))
        cursor.execute("DELETE FROM searchable_books WHERE id = ?",
                       (args["number"],))
    if args["wipe"]:
        cursor.execute("DELETE FROM books")
        cursor.execute("DELETE FROM searchable_books")
    conn.commit()


if __name__ == "__main__":
    connect()
