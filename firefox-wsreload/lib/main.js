/**
  * wsreload Firefox add-on
  * http://github.com/martinec/wsreload/firefox-wsreload
  *
  * License:
  * This Source Code Form is subject to the terms of
  * the Mozilla Public License, v. 2.0. If a copy of
  * the MPL was not distributed with this file, You
  * can obtain one at http://mozilla.org/MPL/2.0/.
  *
  * Authors:
  * Cristian Martinez <me-at-martinec.org>
  */
// jslin moz:true, strict:true
const {Cc,Ci}          = require("chrome");
const tabs             = require("sdk/tabs");
const tabUtils         = require("sdk/tabs/utils");
const timer            = require("sdk/timers");
const simplePrefs      = require("sdk/simple-prefs");
const events           = require("sdk/system/events");
const {MatchPattern}   = require("sdk/util/match-pattern");
const xulapp           = require("sdk/system/xul-app");


const nsIWebNavigation = Ci.nsIWebNavigation;

const HOST             = "127.0.0.1";
const PORT             = "50637";
const END_POINT        = "wsreload";
const POLLING          = 2500;

let highlightColor     = simplePrefs.prefs.highlightColor;
let listening          = simplePrefs.prefs.listening;

let appShellService    = Cc["@mozilla.org/appshell/appShellService;1"].
                         getService(Ci.nsIAppShellService);
let ioService          = Cc["@mozilla.org/network/io-service;1"].
                         getService(Ci.nsIIOService);
let httpHandler        = Cc["@mozilla.org/network/protocol;1?name=http"].
                         getService(Ci.nsIHttpProtocolHandler);
let appInfo            = Cc["@mozilla.org/xre/app-info;1"].
                         getService(Ci.nsIXULAppInfo);
let versionChecker     = Cc["@mozilla.org/xpcom/version-comparator;1"].
                         getService(Ci.nsIVersionComparator);

let ws = null;
let watchedFiles = {};
let watchedTabs  = {};

const ows = {
  xulWindow              : null,
  domWindow              : null,
  wsConstructor          : null,
  create: function () {
    // create a top level hidden window from the add-on itself
    // @source https://gist.github.com/Gozala/4347249
    const uri          = "data:application/xhtml+xml;charset=utf-8,<html/>";
    ows.xulWindow      = appShellService.createTopLevelWindow(
                          null,                              // aParent
                          ioService.newURI(uri, null, null), // aUrl
                          false,                             // aShowWindow
                          false,                             // aLoadDefaultPage
                          null,                              // aChromeMask
                          null,                              // aInitialWidth
                          null,                              // aInitialWidth
                          null);                             // aAppShell


    // Remove the window from the application"s window registry
    appShellService.unregisterTopLevelWindow(ows.xulWindow);

    ows.domWindow      = ows.xulWindow.QueryInterface(Ci.nsIInterfaceRequestor).
                         getInterface(Ci.nsIDOMWindow);

    ows.wsConstructor  = typeof ows.domWindow.WebSocket === "undefined" ?
                         ows.domWindow.MozWebSocket : ows.domWindow.WebSocket;

    console.log("WebSocket interface created");
  },
  destroy: function() {
    if(ows.domWindow) {
      ows.domWindow.close();
      ows.domWindow      = null;
      ows.wsConstructor  = null;
      ows.xulWindow      = null;
      console.log("WebSocket interface destroyed");
    }
  }
};

const wservice = {
  wstimer : null,
  start   : function () {
    ows.create();              // 1
    wservice.connect();        // 2
  },
  stop   : function () {
    wservice.disconnect();     // 2
    ows.destroy();             // 1
  },
  isReady : function () {
    return  ws ? ws.readyState === 1 : false;
  },
  status : function () {
    return  ws ? ws.readyState : 0;
  },
  connect : function() {
    if( !wservice.isReady() ) {
      console.log("Connecting...");
      // try to connect
      try {
        ws = new ows.wsConstructor("ws://" + HOST + ":" + PORT + "/" + END_POINT);
        console.log("WebSocket readyState " + ws.readyState);
        ws.onopen        = wservice.onopen;
        wservice.wstimer = timer.setTimeout(wservice.connect, POLLING);
        return wservice.wstimer;
      }
      catch(ex) {
        console.log("Unable to establish WebSocket connection to " + HOST);
        // wservice.initialized = false;
        return timer.setTimeout(wservice.connect, POLLING);
      }
    }
  },
  disconnect : function() {
    if( wservice.isReady() ) {
       wstab.disconnect();
    }
    try {
      ws.close();
    } catch (ex) {
    }
  },
  send : function( message ) {
    if(wservice.isReady()) {
      console.log("sending " + message);
      return ws.send(message);
    } else {
      console.log("WebSocket isn't ready, unable to send message to " + HOST);
    }
  },
  onopen : function( ) {
    timer.clearTimeout(wservice.wstimer);
    console.log("connection opened");
    console.log("WebSocket readyState " + wservice.status());
    ws.onmessage = wservice.onmessage;
    ws.onclose   = wservice.onclose;
    ws.onerror   = wservice.onerror;
    wservice.send("subscribe|" + httpHandler.userAgent);
    wstab.connect();
  },
  onmessage : function ( event ) {
    if(listening) {
      console.log("message " + event.data);
      let oEvent = JSON.parse(event.data);

      if(oEvent.hasOwnProperty("url")) {
        oEvent.url = encodeURI(oEvent.url);

        let pattern = new MatchPattern(oEvent.url);

        //  loop through all the tabs
        tabUtils.getTabs().forEach(function ( tab ) {
         let browser = tabUtils.getBrowserForTab(tab);
         let url     = browser.currentURI.spec;
         // process only urls that match the message url
         if(pattern.test(url)) {
          let highlighted  = (tab.hasAttribute("wstab-highlighted") &&
                              tab.getAttribute("wstab-highlighted") === "true");
          // Highlighting reloaded tabs excepting the active tab
          if(!tab.selected && !highlighted) {
            // change the tab font color
            tab.style.setProperty("color", highlightColor, "important");
            // set highlighted attribute
            tab.setAttribute("wstab-highlighted", "true");
            // remove highlighting when the tab is select
            tab.addEventListener("TabSelect", function ontabselect() {
              console.log("Reloaded " + url);
              // restore the tab font color
              tab.style.setProperty("color","","important");
              // unset highlighted attribute
              tab.setAttribute("wstab-highlighted", "false");
              // only once
              this.removeEventListener("TabSelect", ontabselect);
            }, false);
          }
          // Reload tab bypassing cache
          browser.reloadWithFlags(nsIWebNavigation.LOAD_FLAGS_BYPASS_CACHE);
         }
        });
      }  // if(oEvent.hasOwnProperty("url"))
    }    // if(listening)
  },
  onclose : function ( ) {
    ws = null;
    console.log("Connection closed");
  },
  onerror : function ( event ) {
    console.log("Socket error unable to establish WebSocket connection to " + HOST);
    try {
      ws.close();
    } catch (ex) {
    }
    return timer.setTimeout(wservice.connect, POLLING);
  }
};

const wsfile = {
  watch: function ( file ) {
    const key   = file;
    const count = (key in watchedFiles) ? watchedFiles[key] + 1 : 1;
    watchedFiles[key] = count;
    if(count === 1) {
      return wservice.send("watch|" + file);
    }
    return true;
  },
  unwatch: function ( file ) {
    const key   = file;
    if(key in watchedFiles) {
      let count = watchedFiles[key] - 1;
      watchedFiles[key] = count;
      if(count === 0) {
        wservice.send("unwatch|" + file);
      }
      return true;
    }
    return false;
  }
};

const wstab = {
  watch: function ( tab ) {
    if(tab.url.indexOf("file://") === 0) {
      const file = decodeURIComponent(tab.url.replace("file://", ""));
      watchedTabs[tab.id] = file;
      return wsfile.watch(file);
    }
    return false;
  },
  unwatch: function ( tabId ) {
    if (tabId in watchedTabs) {
      const file = watchedTabs[tabId];
      watchedTabs[tabId] = null;
      return wsfile.unwatch(file);
    }
    return false;
  },
  onpageshow: function ( tab ) {
    const oldFile = tab.id in watchedTabs ? watchedTabs[tab.id] : null;
    const newFile = decodeURIComponent(tab.url.replace("file://", ""));
    const changed = (oldFile !== newFile);

    if(changed) {
      wstab.unwatch(tab.id);
      wstab.watch(tab);
    }
  },
  onclose: function ( tab ) {
    console.log("tab closed");
    // workaround if tab.id is undefined
    if (typeof tab.id === "undefined") {
      let openTabs = {};
      let openTabId;
      // build a list of open tabs
      for (let index = 0; index < tabs.length; ++index) {
        openTabId = tabs[index].id;
        openTabs[openTabId] = tabs[index];
      }
      // test when an observed tab is closed
      for (let k in watchedTabs) {
        if (!(k in openTabs)) {
          wstab.unwatch(k);
          delete watchedTabs[k];
        }
      }
    }
    else {
      wstab.unwatch(tab.id);
      delete watchedTabs[tab.id];
    }
  },
  onopen: function ( tab ) {
    console.log("open " + tab.url);
    // add this tab to the watched list
    watchedTabs[tab.id] = null;
    // onpageshow
    tab.on("pageshow", wstab.onpageshow);
    // onclose
    tab.on("close", wstab.onclose);
  },
  connect: function () {
    console.log("Watching tabs actions...");
    // Watch all tabs already open
    for (let index = 0; index < tabs.length; ++index) {
      // add this tab to the watched list
      watchedTabs[tabs[index].id] = null;
      // attach onpageshow event
      tabs[index].on("pageshow", wstab.onpageshow);
      // attach onclose event
      tabs[index].on("close", wstab.onclose);
      // watch
      wstab.watch(tabs[index]);
    }
    tabs.on("open", wstab.onopen);
  },
  disconnect : function() {
    console.log("Unwatching tabs actions...");
    // Unwatch all file:// tabs at exit
    for (let index = 0; index < tabs.length; ++index) {
      wstab.unwatch(tabs[index].id);
    }
    // Tab listeners will be removed automatically when the add-on is unloaded
  },
};
// -----------------------------------------------------------------------
exports.main = function (options, callbacks) {
 console.log("addon load");
 wservice.start();
};

exports.onUnload = function (reason) {
  wservice.stop();
  console.log("addon unload");
};
// -----------------------------------------------------------------------
simplePrefs.on("highlightColor", function () {
  console.log("Highlight color preference changed.");
  highlightColor = simplePrefs.prefs.highlightColor;
});

simplePrefs.on("listening", function () {
  console.log("Listening preference changed.");
  listening      = simplePrefs.prefs.listening;
});
// -----------------------------------------------------------------------
// ToggleButton module is only available from Firefox 29 onwards
if(versionChecker.compare(appInfo.version, "29") >= 0) {
  // Known Issues with Toggle Buttons
  // ToggleButton seems have a leak somewhere see Bug 1001833
  // "TypeError: can"t access dead object" due leaks of event/dom module
  // https://bugzilla.mozilla.org/show_bug.cgi?id=1001833
  let { ToggleButton } = require("sdk/ui/button/toggle");

  let wsbutton = {
    active : {
      icon : {
        "16": "./icon-16.png",
        "32": "./icon-32.png",
        "64": "./icon-64.png"
      },
      label : "WSTabReload (listening messages)",
      checked: true,
    },
    inactive : {
      icon : {
        "16": "./icon_inactive-16.png",
        "32": "./icon_inactive-32.png",
        "64": "./icon_inactive-64.png"
      },
      label : "WSTabReload (ignoring messages)",
      checked: false,
    }
  };

  let button = new ToggleButton({
    id:      "wsreload",
    label:   listening ? wsbutton.active.label : wsbutton.inactive.label,
    icon:    listening ? wsbutton.active.icon  : wsbutton.inactive.icon,
    checked: listening,
    onChange: function(state) {
      let toggle     = state.checked ? wsbutton.active : wsbutton.inactive;
      button.icon    = toggle.icon;
      button.label   = toggle.label;
      button.checked = toggle.checked;
      simplePrefs.prefs.listening = state.checked;
      console.log("ToggleButton checked state: " + state.checked);
    }
  });
}
// -----------------------------------------------------------------------
function listener(event) {
  const topic = event.type;
  if (topic === "quit-application-requested") {
    wservice.stop();
    console.log("@quit-application-requested");
  }
  else if(topic === "quit-application-granted") {
    console.log("@quit-application-granted");
  }
  else {
    console.log("@event type : " + topic);
  }
}

events.on("quit-application-requested", listener);
events.on("quit-application-granted", listener);