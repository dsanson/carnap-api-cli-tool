This is a quickly thrown together python script for using the Carnap API to
manage a course.

## Usage

    carnap.py action [args]

Actions:

    ls: list all documents on server
    ls [filename] <[filename]...>: list documents on server with specified [filenames]
    ls ['regex']: list documents on the server with filenames matching 'regex'

    put [files]: upload [files] to server

    get [files]: fetch files from the server by filename
    get ['regex']: fetch files from server with filenames that match regex

    open [files]: open [files] in browser
    open 'regex': open files matching regex in browser

    assns: list all assignments on server

    assn <localopts> [file] <opts> [file] ...: assign each [file] to course with opts
       -d [description]: set description
       -t [n]: set total points to n
       -p [password]: set a password and hide the assignment

    assn <GLOBALOPTS> [files]
       -D [description]: set description to [description] for all [files] 
       -T [n]: set total points to [n] for all [files] 
       -P [password]: set password to [password] for all [files], and hide
          assignment 

    hiddens: list URL and access key for all hidden assignments

    students: list students enrolled in course

    manage: open your Carnap instructor page in browser
    manage assns: open the assignments page 
    manage docs: open the documents page
    manage courses: open the courses page
    manage course: open the course page

    help: show this help

## Examples

### `ls`

    carnap.py ls

Returns a list of documents, showing filename and document id. Note that,

    carnap.py ls Exercise*

will use shell globbing to expand out to include the filenames of all
exercises in your local directory.

    carnap.py ls 'Exercise.*'

Use will list filenames on Carnap that match the regex.

### `put` and `get`

    carnap.py put Exam1 Exam2 Exam3

This will upload the specified documents to Carnap. If a document with that
filename already exists, this will overwrite it.

    carnap.py get Exam1 Exam2 Exam3

This will download the specified documents from Carnap. If a document already
exists locally, this will overwrite it. You can also use a
regex. For example, this will fetch all of your documents from the server:

    carnap.py get '.*'

(Note that the script throttles put and get requests to 1 request per second. So if
you have a lot of files uploaded, this may take a minute.)

### `open`

    carnap.py open Exam1 Exam2

Opens Exam1 and Exam2 in your browser. Note that right now, this always opens
the document page, not the assignment page. I need to add an action or option
for opening the assignment page too.

### `assns`

    carnap.py assns

Returns a list of all assignments. Right now, it is formatted as CSV, and
shows title, total points, password (if any), and description. There is no
built in filtering of results. You can use `grep` for that.

### `assn`


    carnap.py assn Exam1 Exam2

This creates assignments from the uploaded documents with the filenames
'Exam1' and 'Exam2'. If no such documents exist, the command fails. The title
of each assignment is set to the filename of the uploaded document.

You can use options to specify additional assignment properties:

    carnap.py -t 100 -d "First Exam" -p "password" Exam1

This creates an assignment from Exam1, sets the total points to 100, the
description to "First Exam", and the password to "password". Setting a
password also sets the availability of the assignment to hidden.

If an assignment already exists, `assn` can be used to edit its properties,

    carnap.py -t 200 Exam1

`assn` takes local options and global options. Lowercase options are local,
and apply only to the assignment they immediately proceed. For example,

    carnap.py assn -t 100 -d "Unit 12 Test" U12T -t 50 -d "Unit 13 Test" U13T

Uppercase options are global: they apply to every assignment given. They must
occur before anything else on the line. For example, this sets
the total points to 100 for all three exams:

    carnap.py assn -T 100 Exam1 Exam2 Exam3

This can be useful in conjunction with shell globbing. Suppose all the exams
exist in your local directory, are named 'Exam1', 'Exam2', etc., and you want to upload and assign
them all, setting their point values to 100:

    carnap.py put Exam*
    carnap.py assn -T 100 Exam*

A global option can be locally overridden by a local option. For example, 

    carnap.py assn -T 100 Exam1 -t 50 Exam2 Exam3

This sets the total points to Exam1 and Exam3 to 100, but the total points for
Exam2 to 50.

### `hiddens`

    carnap.py hiddens

This will list all assignments that are hidden, in the format:

    https://carnap.io/assignments/[course]/Exam1 access key: mypass1
    https://carnap.io/assignments/[course]/Exam2 access key: mypass2

This can be useful if you need to quickly give a student a link and password
to a given hidden assignment.

### `students`

    carnap.py students

This will give you a list of students enrolled, with some other information.

### `manage`

These are just quick shortcuts for opening Carnap in your browser:

    carnap.py manage
    carnap.py manage assns
    carnap.py manage docs
    carnap.py manage courses
    carnap.py manage course

For the moment, `manage course` is hardcoded to open the page for course "1".
If you are managing more than one course, this may not be the behavior you
want. In any case, it needs to be updated to take advantage of Carnap's
improved API for courses.

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

The config file is a simple YAML file. It needs to define your apikey, your
instructor id, your server, and your course title. For example,

```{.yaml}
---
apikey: YOUR_API_KEY
instructor: rudolf@example.com
server: 'http://localhost:3000'
coursetitle: 'yourcoursetitle'
...
```

If you try to run `carnap.py`, and it can't find a config file, it will
create a template file at `~/.config/carnap.py/config` for you. But you will
still need to edit that file to add the relevant info.
