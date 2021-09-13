This is a quickly thrown together python script for using the Carnap API to
manage a course.

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
    assns: list all assignments on server
    assn <opts> [files|regexes]: assign [files] to course
      <opts>: -d [description]: set description
            -p n: set total points to n
    students: list students enrolled in course
    manage: open the Carnap upload page in browser
    course <number>: open the Carnap course page in browser
    help: show this help

So, for example, assuming you have a file named `U12T` that you want to
upload it:

    carnap.py put U12T

If you want to view it in your browser:

    carnap.py open U12T

If you want to assign it:

    carnap.py assn U12T

If you want to add a description when assigning it:

    carnap.py assn -d "Unit 12 Test" U12T

You can also use the 'assn' command to modify existing assignments. For
example, to add a total points value:

    carnap.py assn -p 100 U12T

And you can assign, or modify, more than one document at a time, with or
without extra parameters:

    carnap.py assn -p 100 -d "Unit 12 Test" U12T -p 50 -d "Unit 13 Test" U13T

Note that the optional parameters must come *before* the assignment they are
mean to modify, and apply *only* to that one assignment.

(I need to add support for other parameters. For now, the only two parameters
supported are total points and description.)

To get a list of all uploaded files:

    carnap.py ls

To get a list of all assignments:

    carnap.py assns

To get a list of all students:

    carnap.py students

To download a file:

    carnap.py get U12T

To download all files with names beginning with 'U2':

    carnap.py get '^U2.*'

Or, to download all files,

    carnap.py get '*'

(Note that this script throttles its requests to 1 request per second. So if
you have a lot of files uploaded, this may take a minute.)


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


