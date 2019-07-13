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

NAME_TYPES = ("first-name", "middle-name", "last-name", "nickname")

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
        raise AttributeError("Include -s or -a flag into your calll")
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


def parse_book(book, location):
    try:
        for event, elem in etree.iterparse(book, events=("end",)):
            # print(elem)
            if event == "end" and "title-info" in elem.tag:
                return parse_book_as_xml(elem.getchildren())
    except Exception as e:
        # parse_malformed_book (idealy)
        with open("log.txt", "a") as log:
            log.write(f"{location} ::: {e}\n")


# for later use, handling malformed files
def parse_malformed_book(book):
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


# ----------- HELPER FUNCTIONS ----------- #


def parse_book_as_xml(children):
    book_info = {
        "author": "",
        "title": "",
        "date": ""
    }
    global counter

    for child in children:
        if child.tag.endswith("author"):
            book_info["author"] = " ".join([name.text for nt in NAME_TYPES
                                            for name in child.getchildren()
                                            if name.tag.endswith(nt)
                                            and name.text])
        if child.tag.endswith("book-title"):
            book_info["title"] = child.text if child.text else ""
        if child.tag.endswith("date"):
            book_info["date"] = child.text if child.text else ""
    counter += 1
    if counter % 1000 == 0:
        print(counter)
    return (book_info["author"], book_info["title"], book_info["date"])


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
    # x = Thread(target=timer, daemon=True)
    # x.start()
    parse_manager()

    print(f"Time elapsed: {time.time() - start}")

    # print(timeit.timeit(testing, number=100000))