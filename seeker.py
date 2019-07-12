from argparse import ArgumentParser
from db_operator import seek_book

parser = ArgumentParser()
parser.add_argument("-a", dest="name")
parser.add_argument("-n", dest="title")
parser.add_argument("-y", dest="date")
args = vars(parser.parse_args())

seek_book(args)