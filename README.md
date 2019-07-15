# fb2lib
Course project for EPAM Python course

Parses fb2 books and stores info into a database.

## How to use:
``docker build -t fb2lib .``

``docker run -t -v [path_to_dir_with_fb2_files]:/data fb2lib``

In interactive shell:

``python3 digger.py -s /data``

``python3 seeker.py -y 1999``

and so on.

``seeker.py`` supports full-text search (include ``-f`` flag when calling it)
