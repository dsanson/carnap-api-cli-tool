This is a quickly thrown together python script for using the Carnap API to
upload and download course documents.

## Usage

    carnap.py action [args]

Actions:

    ls: list all files on server 
    ls 'regex': list files on the server matching 'regex'
    get [files]: fetch files by name from the server
    get 'regex' : fetch files matching regex
    put [files]: upload [files] to server
    open [files]: open [files] in browser
    open 'regex': open files matching regex in browser
    assn: open the Carnap assignment page in browser
    manage: open the Carnap upload page in browser
    course <number>: open the Carnap course page in browser
    help: show this help

So, for example, assuming you have a file named `U12T` that you want to
upload,

    carnap.py put U12T

should upload it. Then, if you want to open the file on Carnap,

    carnap.py open U12T

should open the file in your default web browser.

To download all files with names beginning with 'U2':

    carnap.py get '^U2.*'

Or, to download all files,

    carnap.py get '*'

(Note that this script throttles its requests to 1 request per second. So if
you have a lot of files uploaded, this may take a minute.)

Many of the commands are just shortcuts for opening pages on the Carnap website.

## Installation

I believe that I've got all the requirements in requirements.txt, so you should be able to install any missing requirements with:

```
pip install -r requirements.txt
```

Then just copy `carnap.py` to somewhere in your path.

## Configuration

Before using, you must create a config file, in one of these three
locations:

    ~/.config/carnap.py/config
    ~/.carnap.py
    .carnap.py

The config file is a simple YAML file. It needs to define your apikey, your instructor id, and your server. For example,

```{.yaml}
---
apikey: YOUR_API_KEY
instructor: rudolf@example.com
server: 'http://localhost:3000'
...
```

If you try to run `carnap.py`, and it can't find a config file, it will
create a template file at `~/.config/carnap.py/config` for you. But you will
still need to edit that file to add the relevant info.


