import re
import os
import gzip
import zipfile
import time
from argparse import ArgumentParser
from contextlib import contextmanager
from xml.etree import ElementTree as etree
from db_operator import adder, search_copy


# ----------- SETUP ----------- #

desc = '''
Запустите скрипт с флагом -s для сканирования директории и всех поддиректорий,
с флагом -a для сканирования одного файла. Используйте флаг -u для обновления
информации о записях.
'''

parser = ArgumentParser(description=desc)
path_group = parser.add_mutually_exclusive_group()
path_group.add_argument("-s", dest="dirpath")
path_group.add_argument("-a", dest="bookpath")
parser.add_argument("-u", dest="update", action="store_true")
args = vars(parser.parse_args())

NAME_TYPES = ("first-name", "middle-name", "last-name", "nickname")
DB_WRITING_THRESHOLD = 50000
COUNTER_THRESHOLD = 10000


# ----------- PARSING MANAGERS ----------- #


def parseman_gen(test_path=None):
    '''
    A generator that iterates over all books in the user-defined path.
    It is designed to yield one book at a time.
    :param test_path: overrides all paths, is used for debugging from IDE.
    :return: a single book file
    '''
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
        raise AttributeError("Укажите флаг -s или -a")
    for i in files:
        if i.endswith((".fb2", ".fb2.gz")):
            with open_book(i) as book:
                yield parse_book(book, i)
        elif i.endswith(".fb2.zip"):
            zipped_books = zipfile.ZipFile(i)
            for name in zipped_books.namelist():
                with zipped_books.open(name) as zbook:
                    yield parse_book(zbook, i + f" >>> {name}")
            zipped_books.close()


def parse_manager(test_path=None):
    '''
    The primary function of this module. Iterates over parseman_gen
    and inserts parsing results into database having collected more books
    than set in DB_WRITING_THRESHOLD constant.
    :param test_path: overrides all paths, is used for debugging from IDE.
    '''
    counter = 0
    pg = parseman_gen(test_path)
    books_found = []
    for parsed_book in pg:
        counter += 1
        if counter % COUNTER_THRESHOLD == 0:
            print(counter)
        if parsed_book:
            # creating single-string book representation by joining all
            # parsed info, then combining it with the parsed info for
            # faster insertion
            parsed_book = (" ".join([i for i in parsed_book]),) + parsed_book
            books_found.append(parsed_book)
        if len(books_found) > DB_WRITING_THRESHOLD:
            adder(books_found, True)
            books_found = []
    adder(books_found, True)
    search_copy()


def parse_book(book, location):
    '''
    The general parsing function. Using ElementTree, locates 'title-info'
    node in a book and calls the extraction function, then destroys the built
    tree. Does not parse the whole book.
    If an XML of the book appears to be broken, a special function is called
    in the except block. If this function fails to parse, the error is
    written into log.txt.
    :param book: an opened file with a book
    :param location: location of the book for logging and debugging purposes
    :return: tuple with parsing results
    '''
    try:
        context = iter(etree.iterparse(book, events=("end",)))
        _, root = next(context)
        result = ""
        for event, elem in context:
            if event == "end" and "title-info" in elem.tag and not result:
                result = parse_book_as_xml(list(elem))
                root.clear()
                break
        return result
    except etree.ParseError:
        return parse_malformed_book(book, location)
    except Exception as e:
        with open("log.txt", "a") as log:
            log.write(f"{location} ::: {e}\n")


# ----------- HELPER FUNCTIONS ----------- #


@contextmanager
def open_book(path):
    '''
    Simple context manager that opens a book depending on its format.
    :param path: path to book
    :return: file stream
    '''
    if path.endswith(".fb2"):
        book = open(path, 'rb')
    else:
        book = gzip.open(path)
    yield book
    book.close()


def parse_book_as_xml(title_info):
    '''
    Tries parsing a book using a standard XML library.
    :param title_info: the <title-info> node of the book
    :return: tuple with parsing results
    '''
    author, title, date = "", "", ""
    for node in title_info:
        if node.tag.endswith("author"):
            author = " ".join([name.text for nt in NAME_TYPES
                               for name in list(node)
                               if name.tag.endswith(nt) and name.text])
        if node.tag.endswith("book-title") and node.text:
            title = node.text
        if node.tag.endswith("date") and node.text:
            date = node.text
    return author, title, date


def parse_malformed_book(book, location):
    '''
    Tries to parse a book that violates XML rules. Writes to log if fails.
    :param book: an opened file with a book
    :param location: location of the book for logging and debugging purposes
    :return: tuple with parsing results
    '''
    try:
        book.seek(0)
        first_line = str(book.readline(), encoding="utf-8")
        encoding = re.search('encoding="([^"]*?)"', first_line).group(1)
        book.seek(0)
        desc = ""
        while True:
            desc += str(book.read(1024), encoding)
            if "</title-info>" in desc:
                desc = desc.split("<title-info>")[1].split("</title-info>")[0]
                break
        author = " ".join([i for i in
                           [extract_tag_with_regex(nt, desc)
                            for nt in NAME_TYPES]
                           if i])
        title = extract_tag_with_regex("book-title", desc)
        date = extract_tag_with_regex("date", desc)
        return author, title, date
    except Exception as e:
        with open("log.txt", "a") as log:
            log.write(f"{location} ::: {e}\n")


def extract_tag_with_regex(tag, text):
    '''
    Looks up a node by tag, extracts its text.
    :param tag: FB2 node tag
    :param text: text of title-info node
    :return: text of the looked up node or empty string if nothing is founs
    '''
    if f"<{tag}" in text:
        result = re.search(f"<{tag}[^>]*?>([^<]*?)<", text)
        if result:
            return result.group(1)
    return ""


# ----------- SERVICE FUNCTIONS ----------- #


# parsing a single book
def testing(book_path):
    with open(book_path, "rb") as tbn:
        parse_book(tbn, book_path)


# writes elapsed time to stdout with an interval
def timer():
    start = time.time()
    while True:
        time.sleep(10)
        print(time.time() - start)


# ----------- TEST CONSTANTS ----------- #


SMALLDIR = "C:\\Users\\fatsu\\PycharmProjects\\fb2lib\\test"
BIGDIR = "C:\\Users\\fatsu\\Downloads\\_Lib.rus.ec - Официальная"


if __name__ == "__main__":
    print("Начинаем парсить...")
    start = time.time()
    parse_manager()
    print(f"Прошло секунд: {int(time.time() - start)}")
