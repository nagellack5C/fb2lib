import xml.etree.ElementTree as etree
import re
import os
from argparse import ArgumentParser
from contextlib import contextmanager
import gzip
import zipfile
import time
from threading import Thread
from db_operator import adder

# ----------- PARSING MANAGERS ----------- #

parser = ArgumentParser()
path_group = parser.add_mutually_exclusive_group()
path_group.add_argument("-s", dest="dirpath")
path_group.add_argument("-a", dest="bookpath")
parser.add_argument("-u", dest="update", action="store_true")
args = vars(parser.parse_args())


counter = 0

@contextmanager
def open_book(path):
    if path.endswith(".fb2"):
        book = open(path, 'rb')
    else:
        book = gzip.open(path)
    yield book
    book.close()


def parse_manager():
    books_found = []

    if args["dirpath"]:
        files = []
        walk_gen = os.walk(args["dirpath"])
        for dir in walk_gen:
            for file in dir[2]:
                files.append(os.path.join(dir[0], file))
    elif args["bookpath"]:
        files = [args["bookpath"]]
    else:
        raise AttributeError("Include -s or -a flag into your call")
    for i in files:
        if i.endswith((".fb2", ".fb2.gz")):
            # print(i)
            with open_book(i) as book:
                parsed_book = parse_book(book, i)
                if parsed_book:
                    books_found.append(parsed_book)
        elif i.endswith(".fb2.zip"):
            # print(i)
            zipped_books = zipfile.ZipFile(i)
            for name in zipped_books.namelist():
                # print(name)
                with zipped_books.open(name) as zbook:
                    parsed_book = parse_book(zbook, i + f" >>> {name}")
                    if parsed_book:
                        books_found.append(parsed_book)
        if len(books_found) > 999:
            adder(books_found, args["update"])
            books_found = []
    adder(books_found, args["update"])


book_infos = []

def parse_book(book, location):
    # print(location)
    book_info = {
        "author": "",
        "title": "",
        "date": ""
    }
    global counter

    try:
        for event, elem in etree.iterparse(book, events=("end",)):
            # print(elem)
            if event == "end" and "title-info" in elem.tag:
                children = elem.getchildren()
                for child in children:
                    if child.tag.endswith("author"):
                        author = {
                            "first-name": "",
                            "middle-name": "",
                            "last-name": "",
                            "nickname": ""
                        }
                        for name in child.getchildren():
                            name_kind = re.match('\{.*\}(.*)', name.tag).group(1)
                            if name_kind in author:
                                author[name_kind] = name.text
                        author_name = []
                        names = ["first-name", "middle-name", "last-name"]
                        for name in names:
                            if author[name]:
                                author_name.append(author[name])
                        if not author_name and author["nickname"]:
                            author_name = author["nickname"]
                        book_info["author"] = " ".join(author_name)
                    if child.tag.endswith("book-title"):
                        book_info["title"] = child.text if child.text else ""
                    if child.tag.endswith("date"):
                        book_info["date"] = child.text if child.text else ""
                counter += 1
                if counter % 1000 == 0:
                    print(counter)
                    # print(book_info)
                break
        book_info = (book_info["author"], book_info["title"], book_info["date"])
        # print(book_info)
        return book_info
    except Exception as e:
        with open("log.txt", "a") as log:
            log.write(f"{location} ::: {e}\n")

# for later use, handling malformed files
def parse_book_alt(book):
    book.seek(0)
    first_line = str(book.readline(), encoding="utf-8")
    print(first_line)
    encoding = re.search('encoding="([^"]*?)"', first_line).group(1)
    # print(encoding.group(1))

    desc = b""
    for i in book:
        desc += i
        if b"</title-info>" in i:
            break
    desc = str(desc, encoding=encoding) + "</FictionBook>"
    print(desc)


# ----------- SERVICE FUNCTIONS ----------- #


def testing(book):
    with open(book, "rb") as tbn:
        parse_book(tbn)


def timer():
    start = time.time()
    while True:
        time.sleep(10)
        print(time.time() - start)


if __name__ == "__main__":
    start = time.time()
    x = Thread(target=timer, daemon=True)
    x.start()
    parse_manager()

    print(f"Time elapsed: {time.time() - start}")

    # print(timeit.timeit(testing, number=100000))