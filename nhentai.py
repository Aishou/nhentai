#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Copyright (c) 2016, Aishou (kaito.linux@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import urllib.request
from urllib.request import Request, urlopen
from requests import get
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import argparse

def print_header():
    longstring = """\
      _               _        _
._ _ | |_  ___ ._ _ _| |_ ___ <_>    ___  _ _
| ' || . |/ ._>| ' | | | <_> || | _ | . \| | |
|_|_||_|_|\___.|_|_| |_| <___||_|<_>|  _/`_. |
                                    |_|  <___'
"""
    print(longstring)

def job(url, manga_name):
    def download(url, file_name, manga_name):

        if not os.path.exists(manga_name):
            os.makedirs(manga_name)

        # That Unicode Stuff sucks so hard...
        save_path = os.path.dirname(os.path.realpath(__file__)) + '/' + manga_name.decode('utf-8') + '/'

        print("Download URL: ", url)
        with open(os.path.join(save_path, file_name), "wb") as file:
            response = get(url)
            file.write(response.content)

    try:
        # Get HTTP Status Code
        # nhentai uses not only jpg.. argh
        # if 404 try some other Formats...
        # TODO: Rework this to read format out of HTML..

        #print(manga_name)
        formats = ["jpg", "png", "gif"]

        for i in formats:
            url_temp = url + i
            http_code  = requests.head(url_temp).status_code
            #print ("HTTP Code: ", http_code)
            if http_code == 200: # OK
                url = url_temp
                file_name = str(url.split('/')[-1])
                download(url, file_name, manga_name)

    except requests.ConnectionError:
        print("failed to connect")

def work(hentai):
    req = Request(hentai, headers={'User-Agent': 'Mozilla/5.0'}) # Need User Agent.. (403)
    page = urlopen(req).read()
    soup = BeautifulSoup(page, "lxml")

        # Getting Basic Info about doujinshi...
    manga_name      = soup.find("div", {"id": "info"}).h1.text.encode('utf-8')
    manga_pages     = int(soup.find("div", {"id": "info"}).find_all('div')[7].text.split(' ')[0])
    manga_image_id  = int(soup.find("div", {"id": "cover"}).img['src'].split('/')[4])

    print("Manga:    ", manga_name.decode('utf-8'))
    print("Pages:    ", manga_pages)
    print("Image ID: ", manga_image_id)

    manga_urls = []

    for i in range(1, manga_pages+1):
        manga_url = "http://i.nhentai.net/galleries/{0}/{1}.".format(manga_image_id, i)
        manga_urls.append(manga_url)


    executor = concurrent.futures.ProcessPoolExecutor()
    futures = [executor.submit(job, manga_url, manga_name) for manga_url in manga_urls]
    concurrent.futures.wait(futures)


#    print(futures[0].done())
#    sleep(5)
#    print(futures[0].done())
#    print(futures[0].result())

if __name__ == "__main__":

    print_header()
    #Command line arguement parser
    parser = argparse.ArgumentParser(description='https://nhentai.net/g/xxxx')
    parser.add_argument('URL', help='https://nhentai.net/g/xxxx')
    args = vars(parser.parse_args())

    print(args['URL'])
    if args['URL'].startswith("https://nhentai.net/g/") or args['URL'].startswith("http://nhentai.net/g/"):
        hentai = args['URL']
        if hentai.split('/')[4]:
            if hentai.split('/')[4].isnumeric():
                work(hentai)
        else:
            print("doujinshi URL Error.")
            quit()
    else:
        print("doujinshi URL Required.")
        quit()
