# fb2lib
Course project for EPAM Python course

Parses fb2 books and stores info into a database.

## How to use:
``docker pull nagellack5c/fb2lib``

``docker run -it -v [path_to_dir_with_fb2_files]:/data nagellack5c/fb2lib``

In interactive shell:

``python3 digger.py -s /data``

``python3 seeker.py -y 1999``

and so on.

``seeker.py`` supports full-text search (include ``-f`` flag when calling it)

**Requires Python 3.7!**
