/*     wsreload - Reload your tabs !
 *     Copyright (C) 2012 Florian Mounier <paradoxxx.zero@gmail.com>
 *
 *     This program is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU Affero General Public License as
 *     published by the Free Software Foundation, either version 3 of the
 *     License, or (at your option) any later version.
 *
 *     This program is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU Affero General Public License for more details.
 *
 *     You should have received a copy of the GNU Affero General Public License
 *     along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var connect, polling = 2500,
    host = '127.0.0.1',
    port = 50637,
    endpoint = 'wsreload';
var onopen = function (event) {
    console.log('Connection opened');
};

var onmessage = function (event) {
    console.log(event.data);
    chrome.tabs.query(JSON.parse(event.data), function(tabs) {
        for(var i = 0; i < tabs.length ; i++) {
            var tab = tabs[i];
            console.log('>' + tab);
            chrome.tabs.reload(
                tab.id, {bypassCache: true},
                (function() {
                    var this_tab = this;
                    console.log('Reloaded ' + this_tab.title);
                }).bind(tab));
        }
        chrome.windows.getAll(function (windows) {
            for(var i = 0; i < windows.length ; i++) {
                var window = windows[i];
                chrome.tabs.query(
                    {windowId: window.id, active: true},
                    (function (active_tabs) {
                        var win = this;
                        var active_tab = active_tabs[0];
                        var to_highlight = tabs.filter(
                            function (tab) { return tab.windowId == win.id; }
                        ).map(
                            function (tab) { return tab.index; }
                        );
                        to_highlight.unshift(active_tab.index);
                        chrome.tabs.highlight(
                            {windowId: win.id, tabs: to_highlight},
                            function () {});
                    }).bind(window));
            }
        });
    });
};

var onclose = function (event) {
    console.log('Connection closed');
    setTimeout(connect, polling);
};


connect = function() {
    console.log('Connecting');
    var ws = new WebSocket('ws://' + host + ':' + port + '/' + endpoint);
    if(ws.readyState == 3) {
        console.log('Failed ');
        setTimeout(connect, polling);
        return;
    }
    ws.onopen = onopen;
    ws.onmessage = onmessage;
    ws.onclose = onclose;
};

connect();
