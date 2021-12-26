This is a quickly thrown together python script for using the Carnap API to
manage a course.

## Usage

Usage:

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

The `ls` command is used to list documents on the Carnap server:

    carnap.py ls

Returns a list of documents, showing both filename and document id. Optionally, you
can supply a list of filenames, and it will restrict the list to those files:

    carnap.py ls 01R 01E

Or you can supply a regular expression, and it will restrict the list to files
that match the regular expression:

    carnap.py ls '01.*'

Note that you must put the regular expression in quotes to avoid shell
globbing.

### `put` and `get`

The `put` and `get` commands are used to upload and download documents from
the Carnap server:

    carnap.py put 01R

This will upload the local file named `01R` to Carnap. If a document named
`01R` already exists on the Carnap server, this will overwrite that document.

    carnap.py get 01R

This will download the file named `01R` from Carnap. If a document named `01R` already
exists locally, this will overwrite it. 

`put` and `get` be supplied a list of files. And `get` can also take a regular
expression:

    carnap.py put 01R 01E
    carnap.py put 01*

That second example will use shell globbing to upload all local files
beginning with `01`.

    carnap.py get 01R 01E
    carnap.py get '01.*'
    carnap.py get '.*'

Note once again that you need to put any regular expression into quotes to
avoid shell globbing.

### `open`

The `open` command opens a document that is on Carnap's server in your
browser:

    carnap.py open 01R

Note that it opens the "shared document" page, not the "assignment" page. The
`open` command can also take a list of document names, or a regular
expression.

### `assns`

The `assns` command returns a list of all your course assignments.

    carnap.py assns

Each assignment is listed as follows:

    01R,80,,Chapter 1 Reading

This is comma delimited: the first item, `01R`, is the name of the assignment.
The second item is the total points. The third item is the access key, if any.
The fourth is the assignment description.

### `assn`

The `assn` command is used to create an assignments from documents already
uploaded to Carnap.

    carnap.py assn 01R

This creates an assignment from the document named `01R`. If no such document
exists on Carnap's server, the command fails. So a simple workflow might be:

    carnap.py put 01R
    carnap.py assn 01R

You can use options to specify additional assignment properties:

    carnap.py -t 100 -d "First Exam" -p "password" 01E

This creates an assignment from `01E`, setting the total points to 100, the
description to "First Exam", and the password to "password". Setting a
password also sets the availability of the assignment to hidden.

**Note**: specifying multiple options at the same time seems to be broken?
Workaround:

    carnap.py -t 100 01E
    carnap.py -d "First Exam" 01E
    carnap.py -p "password" 01E

If an assignment already exists, `assn` can be used to edit its properties,

    carnap.py -t 200 01E

The `assn` command can be used to create several assignments at once:

    carnap.py assn 01R 01E 01T

When creating several assignments, options can be specified as "global" or
"local". Lowercase options are local,
and apply only to the assignment they immediately proceed. For example,

    carnap.py assn -t 100 -d "Unit 12 Test" 12T -t 50 -d "Unit 13 Test" 13T

Uppercase options are global, and apply to every assignment created. They must
occur before anything else on the line:

    carnap.py assn -T 100 Midterm1 Midterm2 Midterm3

A global option can be locally overridden by a local option. For example, 

    carnap.py assn -T 100 Midterm1 -t 50 Midterm2 Midterm3

### `hiddens`

The `hiddens` command lists all assignments that are "hidden", in a format
that allows for easy cutting and pasting, to share with students:

    carnap.py hiddens

    https://carnap.io/assignments/[course]/01T-makeup access key: mypass1
    https://carnap.io/assignments/[course]/02T-makeup access key: mypass2

I offer my students lots of "retake" opportunities by creating alternate
hidden versions of given assignments. When a student asks for a retake, I just
run `carnap.py hiddens`, cut and paste the appropriate line, and send it to
them.

### `students`

    carnap.py students

This will give you a list of enrolled students, with some other information.

### `manage`

These are just quick shortcuts for opening Carnap pages in your browser:

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

Clone this repository, and cd into the directory:

```
git clone https://github.com/dsanson/carnap-api-cli-tool
cd carnap-api-cli-tool
```

Use `pip` to install any dependencies:

```
pip install -r requirements.txt
```

Then copy `carnap.py` to somewhere in your path.

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

So, for example, my config file looks like this:

```{.yaml}
---
apikey: MY_API_KEY
instructor: 'dsanson@...com'
server:  'https://carnap.io'
coursetitle: 'ISU_112_FALL_2021'
...
```

You can find your API key at the bottom of the "Manage Uploaded Documents" tab
on Carnap.

If you try to run `carnap.py`, and it can't find a config file, it will
create a template file at `~/.config/carnap.py/config` for you. But you will
still need to edit that file to add the relevant info.
