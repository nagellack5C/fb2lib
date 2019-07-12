import sqlite3


def connect(create=None):
    conn = sqlite3.connect("mydatabase.sqlite")
    cursor = conn.cursor()

    if create:
        # cursor.execute("""CREATE TABLE books
        #                    (title TEXT, first_name TEXT, middle_name TEXT, last_name TEXT,
        #                    nickname TEXT, year INT)
        #                """)

        cursor.execute("""CREATE TABLE books
                                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                   title TEXT, name TEXT, date INT)
                               """)

        conn.commit()

    return (conn, cursor)


def adder(books_found, update):
    conn, cursor = connect()
    # print(books_found)

    print(update)
    if update:
        cursor.executemany("INSERT OR ROLLBACK INTO books(name, title, date) VALUES (?,?,?)", books_found)
    else:
        cursor.executemany("INSERT INTO books(name, title, date) VALUES (?,?,?)", books_found)
    conn.commit()

def seek_book(args):
    conn, cursor = connect()
    print(args)

    new_args = []

    query = "SELECT * FROM books WHERE "
    q_vals = []
    # values = " VALUES ("
    for arg in ["name", "title", "date"]:
        if args[arg]:
            q_vals.append(f"{arg} = ?")
            new_args.append(args[arg])
    new_args = tuple(new_args)
    # values += ",".join(["?" for i in q_vals]) + ")"
    query = query + " AND ".join(q_vals)
    print(query)
    print(new_args)

    cursor.execute(query, new_args)
    for i in cursor.fetchall():
        print(i)

def deleter(args):
    conn, cursor = connect()

    if args["number"]:
        cursor.execute("DELETE FROM books WHERE id = ?", (args["number"],))
    if args["wipe"]:
        cursor.execute("DELETE FROM books")
    conn.commit()

def flush():
    conn = sqlite3.connect("mydatabase.sqlite")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE books")
    conn.commit()


# Вставляем множество данных в таблицу используя безопасный метод "?"
# albums = [('Exodus', 'Andy Hunter', '7/9/2002', 'Sparrow Records', 'CD'),
#           ('Until We Have Faces', 'Red', '2/1/2011', 'Essential Records', 'CD'),
#           ('The End is Where We Begin', 'Thousand Foot Krutch', '4/17/2012', 'TFKmusic', 'CD'),
#           ('The Good Life', 'Trip Lee', '4/10/2012', 'Reach Records', 'CD')]
#
# cursor.executemany("INSERT INTO albums VALUES (?,?,?,?,?)", albums)
if __name__ == "__main__":
    # flush()
    connect(create=True)