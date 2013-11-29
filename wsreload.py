#!/usr/bin/env python
# -*- coding: utf-8 -*-

#     wsreload - Reload your tabs !
#     Copyright (C) 2012 Florian Mounier <paradoxxx.zero@gmail.com>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
from wsreload.client import sporadic_reload, watch, unwatch
import argparse
import os


chrome_parser = argparse.ArgumentParser(
    add_help=False,
    description='Chrome tab filter options')

chrome_parser.add_argument(
    '--active', dest='active', type=bool,
    help='Whether the tabs are active in their windows.')

chrome_parser.add_argument(
    '--pinned', dest='pinned', type=bool,
    help='Whether the tabs are pinned.')

chrome_parser.add_argument(
    '--highlighted', dest='highlighted', type=bool,
    help='Whether the tabs are highlighted.')

chrome_parser.add_argument(
    '--status', dest='status', type=str,
    choices=["loading", "complete"],
    help='Whether the tabs have completed loading.')

chrome_parser.add_argument(
    '--title', dest='title', type=str,
    help='Match page titles against a pattern.')

chrome_parser.add_argument(
    '--url', dest='url', type=str,
    help='Match tabs against a URL pattern.')

chrome_parser.add_argument(
    '--windowId', dest='windowId', type=int,
    help='The ID of the parent window, '
    'or chrome.windows.WINDOW_ID_CURRENT for the current window.')

chrome_parser.add_argument(
    '--windowType', dest='windowType', type=str,
    choices=["normal", "popup", "panel", "app"],
    help='The type of window the tabs are in.')

chrome_parser.add_argument(
    '--index', dest='index', type=int,
    help='The position of the tabs within their windows.')

chrome_parser.add_argument(
    '--delay', dest='delay', type=int,
    help='Delay to wait before refreshing.')

parser = argparse.ArgumentParser(
    description='Reload all tabs matching query through websocket',
    prog='wsreload',
    parents=(chrome_parser,))

parser.add_argument('-H', '--host', dest='host', type=str, default='127.0.0.1')
parser.add_argument('-P', '--port', dest='port', type=int, default=50637)
parser.add_argument('-E', '--endpoint', dest='endpoint',
                    type=str, default='wsreload')

parser.add_argument(
    '--watch', dest='watch', nargs='+',
    help='Tell the server to watch files '
    'and reload according to the other options')

parser.add_argument(
    '--unwatch', dest='unwatch',  nargs='+',
    help='Tell the server to unwatch the following files')

query, _ = chrome_parser.parse_known_args()
query = dict(filter(lambda x: x[1] is not None, vars(query).items()))

opts = parser.parse_args()


if opts.watch:
    files = list(map(lambda x: os.path.abspath(x), opts.watch))
    watch(query, files, opts.host, opts.port, opts.endpoint)
elif opts.unwatch:
    files = list(map(lambda x: os.path.abspath(x), opts.unwatch))
    unwatch(files, opts.host, opts.port, opts.endpoint)
else:
    sporadic_reload(query, opts.host, opts.port, opts.endpoint)
