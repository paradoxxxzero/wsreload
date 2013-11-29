# wsreload - Reload your tabs !
#   Copyright (C) 2012 Florian Mounier <paradoxxx.zero@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
polling = 2500
host = "127.0.0.1"
port = 50637
endpoint = "wsreload"
watched_files = {}


onopen = ->
    console.log "Connection opened"
    send "subscribe|#{navigator.userAgent}"

    # Getting all tabs at start
    chrome.tabs.query {}, (tabs) ->
        for tab in tabs
            # Checking for local files
            if tab.url.indexOf('file://') is 0
                watched_files[tab.id] = tab.url
                send "watch|#{tab.url}"

# Synchronise opened local files and watched files
chrome.tabs.onUpdated.addListener (tabId, changeInfo, tab) ->
    return unless changeInfo.url
    url = changeInfo.url
    if tabId of watched_files
        send "unwatch|#{watched_files[tabId]}"

    return unless url.indexOf('file://') is 0
    watched_files[tabId] = url
    send "watch|#{url}"

chrome.tabs.onRemoved.addListener (tabId, removeInfo) ->
    if tabId of watched_files
        send "unwatch|#{watched_files[tabId]}"

onmessage = (event) ->
    console.log event.data
    eventobj = JSON.parse(event.data)
    chrome.tabs.query eventobj, (tabs) ->
        # Reloading tabs
        for tab in tabs
            chrome.tabs.reload(tab.id, bypassCache: true, (-> console.log "Reloaded #{@title}").bind(tab))
        # Highlighting reloaded tabs
        # Must be done all at once per window
        chrome.windows.getAll (windows) ->
            for win in windows
                chrome.tabs.query
                    windowId: win.id
                    active: true
                , ((active_tabs) ->
                    active_tab = active_tabs[0]
                    to_highlight = tabs
                        .filter((tab) => tab.windowId is @id)
                        .map((tab) -> tab.index)
                    to_highlight.unshift active_tab.index
                    chrome.tabs.highlight
                        windowId: @id
                        tabs: to_highlight
                    , (->)).bind(win)


onclose = ->
    console.log "Connection closed"
    setTimeout connect, polling


connect = ->
    console.log "Connecting"
    window.ws = new WebSocket("ws://#{host}:#{port}/#{endpoint}")
    if ws.readyState is 3
        console.log "Failed"
        setTimeout connect, polling
        return
    ws.onopen = onopen
    ws.onmessage = onmessage
    ws.onclose = onclose


send = (message) ->
    console.log "Sending #{message}"
    ws.send message


connect()
