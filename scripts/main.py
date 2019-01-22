#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import deque
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import sqlite3
from datetime import datetime


parser = False

url_table = {}
sql_rows = []

# arguments part
parser = ArgumentParser()
parser.add_argument("--load", "-l", dest="load",
                    help="write site url for load new site")
parser.add_argument("--get", "-g", dest="get",
                    help="write site url to get links")
parser.add_argument("--depth", dest="depth", help="write depth of search")
parser.add_argument("-n", dest="number", help="write number of links")
args = parser.parse_args()

if args.depth:
    max_level = int(args.depth)
if args.number:
    number_of_urls = int(args.number)


if not parser:
    url = "http://www.python.org"

if not parser:
    max_level = 2
if not parser:
    number_of_urls = 2


def getURL(page):
    """
    :param page: html of web page
    :return: urls in that page
    """
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote


def beautiful_result(url):
    try:
        response = requests.get(url)
    except Exception as e:
        response = requests.get(url, verify=False)
    # parse html
    beautiful_soup_result = BeautifulSoup(response.content)
    return beautiful_soup_result.title.next, str(beautiful_soup_result)


def save_page(page, url_table, search_queue, level, base_url):
    url, n = getURL(page)
    page = page[n:]
    if url:
        if not url.startswith('http') and not url.startswith('#'):
            if base_url[-1] == '/':
                url = base_url[:-1] + url
            else:
                url = base_url + url

            '''если оставить на этом уровне, то будут только для сайта уровни, 
            если спустить на уровень ниже (убрать один таб), то захватит и другие сайты
            '''
            if url not in url_table:
                # print(url)
                url_table[url] = {}
                url_table[url]['level'] = level
                if level < max_level:
                    search_queue += [url]
                else:
                    return

        save_page(page, url_table, search_queue, level, base_url)


def load(url_table, sql_rows):
    start = datetime.now()
    title, page = beautiful_result(url)

    # sql
    conn = sqlite3.connect('pages.db')
    c = conn.cursor()

    # # Create table if not exists
    try:
        c.execute('''CREATE TABLE urls
                (url text, title text, html text, parent text)''')
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()

    url_table[url] = {}
    url_table[url]['level'] = 0
    url_table[url]['title'] = title
    url_table[url]['page'] = page

    search_queue = deque()
    search_queue += [url]
    parent = url

    while search_queue:
        base_url = search_queue.popleft()
        title, page = beautiful_result(base_url)
        url_table[base_url]['title'] = title
        url_table[base_url]['page'] = page

        sql_rows.append((base_url, title, page, parent))

        next_level = url_table[base_url]['level'] + 1
        save_page(page, url_table, search_queue, next_level, base_url)

    sql_rows
    conn = sqlite3.connect('pages.db')
    c = conn.cursor()
    c.executemany('insert into urls values (?,?,?,?)', sql_rows)
    conn.commit()
    conn.close()

    finish = datetime.now()
    print(f'OK, process finished in {(finish-start).seconds} seconds')


def get(url, number):
    conn = sqlite3.connect('pages.db')
    c = conn.cursor()

    t = (url, number)
    c.execute('SELECT DISTINCT * FROM urls WHERE parent=? LIMIT ?', t)
    for row in c.fetchall():
        print(f'{row[0]}: \'{row[1]}\'')

    conn.close()


# load(url_table, sql_rows)
# get(url, number_of_urls)


if args.get:
    url = args.get
    get(url, number_of_urls)
else:
    url = args.load
    load(url_table, sql_rows)


# check lvls of urls
# for key, value in url_table.items():
#     level_val = value['level']
#     if 'title' in value:
#         title_val = value['title']
#     print(f'{key}: {title_val}, lvl: {level_val}')
