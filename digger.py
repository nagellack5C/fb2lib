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
import tracemalloc
import gc

# ----------- PARSING MANAGERS ----------- #

tracemalloc.start()

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

def packer(book):
    books = yield
    while True:
        books.append(book)

def parseman_gen(test_path=None):
    if test_path:
        args["dirpath"] = test_path
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
                yield parse_book(book, i)
        elif i.endswith(".fb2.zip"):
            zipped_books = zipfile.ZipFile(i)
            for name in zipped_books.namelist():
                with zipped_books.open(name) as zbook:
                    yield parse_book(zbook, i + f" >>> {name}")
            zipped_books.close()


def parse_manager(test_path=None):
    pg = parseman_gen(test_path)
    bf = []
    for pb in pg:
        if pb:
            bf.append(pb)
        if len(bf) > 1000:
            print("wtf")

            # gc.collect()
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)
            adder(bf, args["update"])
            del bf
            bf = []
    adder(bf, args["update"])
    # bf = [pb for pb in pg if pb]
    # adder(bf, args["update"])


def parse_book(book, location):
        print(location)
    # try:
        # context = iter(etree.iterparse(book, events=("end",)))
        # _, root = next(context)
        # print("root: ", next(etree.iterparse(book)))
        # print("root: ", root)
        result = ""
        for event, elem in etree.iterparse(book, events=("end",)):
            # print("elem: ", elem)
            if event == "end" and "title-info" in elem.tag and not result:
                # print(elem.getchildren())
                result = parse_book_as_xml(elem.getchildren())
                # etree.dump(root)
                # root.clear()
                # etree.dump(root)
                # print(root.children())
                # elem.clear()
                # del context
                book.seek(-14, 2)
                print(book.tell())
                print(book.read())
        return result
    # except Exception as e:
    #     print(e)
    #     # parse_malformed_book (ideally)
    #     with open("log.txt", "a") as log:
    #         log.write(f"{location} ::: {e}\n")


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
    # print(counter)

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
        # child.clear()
    counter += 1
    if counter % 1000 == 0:
        print(counter)
    # etree.dump(children)
    # print(children)
    # children.clear()
    # print(children)
    # etree.dump(children)
    # print(book_info)


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


# ----------- TEST CONSTANTS ----------- #
SMALLDIR = "C:\\Users\\fatsu\\PycharmProjects\\fb2lib\\test"
BIGDIR = "C:\\Users\\fatsu\\Downloads\\_Lib.rus.ec - Официальная"


if __name__ == "__main__":
    start = time.time()
    x = Thread(target=timer, daemon=True)
    x.start()
    parse_manager(test_path=SMALLDIR)

    print(f"Time elapsed: {time.time() - start}")

    # print(timeit.timeit(testing, number=100000))