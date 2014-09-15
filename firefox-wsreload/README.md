# WSTabReload Firefox Addon 

> Forget about the `[F5]` key! WSTabReload is a web development productivity tool that will help you to automatically reload your browser tabs every time selected local files are changed.

![](screenshot.png)

## Requirements:
* [WSReload][] Server.
* [Firefox 26][]+
* GNU/Linux.

## Installation

Install from the [Firefox Add-ons site](https://addons.mozilla.org/en-US/firefox/addon/wstabreload/).

## Build

To manually build the extension bundle (`.xpi`) from the source type :

    make

This command will produce a file named `firefox-wsreload.xpi`. You can simply drag and drop it on Firefox to install the Add-on.

## Usage

* Install the [WSReload][] Server.
```
  $ pip install wsreload
```
  
* Start the server using:
```
  $ wsreload-server &
```
  
* Use a tab reloading criteria :
    - *file://* : Every local file opened in your browser with a `file://` scheme will be automatically synchronized.
    - *matching*: Reload all tabs that match a pattern, e.g.
    ```    
        $ wsreload --watch foo/bar --url "http://localhost:8080/*"
    ```        
    Tells the browser to reload all tabs that match the following url pattern : `http://localhost:8080/*` whenever a file in the `foo/bar` directory is modified. 

## Related

Also available on [Chrome](https://chrome.google.com/webstore/detail/wsreload/knefplbckfcppebehbomeankfgjalmak).

## Contribute

Start by grabbing the code using Git. If you're planning to contribute, fork the project on GitHub.

## License

Free use of this software is granted under the terms of the MPL License.

## About

- Firefox extension written by Cristian Martinez <me@martinec.org>
- [WSReload][] author is Florian Mounier <paradoxxx.zero@gmail.com>

----

For more information see the [WSReload][] homepage.

  [WSReload]:   https://github.com/paradoxxxzero/wsreload
  [Firefox 26]: http://www.mozilla.com/en-US/firefox/fx/
