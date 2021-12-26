#!/usr/bin/env python3
"""\
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
"""

import requests
import sys
import re
import os.path
import time
from pathlib import Path
import yaml
import webbrowser

# Load config file

dummy_apikey = '<apikey>'
dummy_instructor = 'rudolf@example.com'
default_server = 'http://localhost:3000'
default_course = '<course title>'

config_template=f'''\
---
apikey: {dummy_apikey}
instructor: {dummy_instructor}
server: {default_server}
coursetitle: {default_course}
...'''

home = Path.home()
current = Path('.')

config = False
for f in [ 
    home / '.carnap.py',
    home / '.config' / 'carnap.py' / 'config', 
    current / '.carnap.py'
     ]:
  if f.exists():
    with open(f,'r') as ymlfile:
       cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
 
    apikey = cfg['apikey']
    instructor = cfg['instructor']
    server = cfg['server']
    coursetitle = cfg['coursetitle']
    config = True

if config:
  if apikey == dummy_apikey or instructor == dummy_instructor:
    print(f'You must add your APIKEY and instructor ID to the configuration file.')
    raise SystemExit

else:
  print('No configuration file found.')
  folder = (home / '.config' / 'carnap.py')
  folder.mkdir(parents=True, exist_ok=True)
  cfg = folder / 'config'
  cfg.write_text(config_template)   

  print(f'Configuration template created at {str(cfg)}')
  print(f'You must add your APIKEY and instructor ID to this file.')
  raise SystemExit


base = f'{server}/api/v1'

# Basic functions for communicating with Carnap

def rq(meth, p, *args, key=apikey, **kwargs):
  h = {
    'X-API-KEY': key,
  }
  return requests.request(meth, base + p, *args, **kwargs, headers=h)

def get_metadata():
  return rq('GET', f'/instructors/{instructor}/documents').json()

def get_file(id):
  return rq('GET', f'/instructors/{instructor}/documents/{id}/data').text

def create_remote_document(params):
  return rq('POST', f'/instructors/{instructor}/documents',
         json=params
      ).json()

def upload_document(i,content):
  rq('PUT', f'/instructors/{instructor}/documents/{i}/data', 
      data=content.encode('utf-8'))

def update_document(i,params):
  return rq('PATCH', 
            f'/instructors/{instructor}/documents/{i}',
            json=params
         ).json()

def assign_document(params):
  return rq('POST', 
            f'/instructors/{instructor}/courses/{coursetitle}/assignments',
            json=params
         ).json()

def patch_assignment(assn_id,params):
  return rq('PATCH', 
            f'/instructors/{instructor}/courses/{coursetitle}/assignments/{assn_id}',
            json=params
         ).json()

def get_assignments():
  return rq('GET', f'/instructors/{instructor}/courses/{coursetitle}/assignments').json()

def get_students():
  return rq('GET', f'/instructors/{instructor}/courses/{coursetitle}/students').json()

def fetch_scores(student_id):
  return rq('GET', 
            f'/instructors/{instructor}/courses/{coursetitle}/students/{student_id}/submissions'
         ).json()

def fetch_accesses(student_id):
  return rq('GET',
            f'/instructors/{instructor}/courses/{coursetitle}/students/{student_id}/assignmentTokens'
         ).json()

# Helper functions

def throttle(first):
  if not first:
    time.sleep(1)
  return False

def get_file_id(docs,f):
  i = None
  for item in docs:
    if item['filename'] == f:
      i = item['id']
  return i

def get_doc_by_id(docs,id):
  d = None
  for doc in docs:
    if doc['id'] == id:
      d = doc
  return d

def get_assn_id(assns,f):
  i = None
  for assn in assns:
    if assn['title'] == f:
      i = assn['id']
  return i

def get_assn_by_title(assns,f):
  a = None
  for assn in assns:
    if assn['title'] == f:
      a = assn
  return a

def get_assn_title(assns,id):
  title = None
  for assn in assns:
    if assn['id'] == id:
      title = assn['title']
  return title

def get_student_ids(students,query):
  results = []
  for student in students:
    if student['universityId'] and re.match(query, student['universityId']):
      results.append(student['id'])

  return results


# Actions

def list_documents(docs, args):
  if len(args) == 0:
    for item in docs:
        print(f"{item['id']}: {item['filename']}")
  else:
    for arg in args:
        for item in docs:
          if re.match(arg, item['filename']):
            print(f"{item['id']}: {item['filename']}")

def list_assignments(assns):
    for assn in assns:
        title = assn["title"]
        points = assn["pointValue"]
        description = assn["description"]
        availability = assn["availability"]
        if not points:
          points = ""
        if not description:
          description = "" 
        if availability:
          password = availability['contents']
        else:
          password = ""

        print(f'{title},{points},{password},{description}')

def list_hiddens(assns):
  for assn in assns:
    availability = assn["availability"]
    if availability:
      password = availability['contents']
      file = assn['title']
      url = f'https://carnap.io/assignments/{coursetitle}/{file}' 
      print(f'{url} access key: {password}')

def list_attempts(students,assns,args):
  for student in args:

    student_id = get_student_ids(students,student)
    accesses = fetch_accesses(student_id)
    for access in accesses:
      title = get_assn_title(assns,access['assignment'])
      print(f'{title}: {access["createdAt"]}')

def list_students(students):
    for student in students:
        print(f'{student["lastName"]},{student["firstName"]},{student["universityId"]},{student["email"]},{student["id"]}')

def get_scores(students,assns,args):
  if len(args) == 0:
    print_help()
 
  student_ids = []

  for query in args:
    student_ids = get_student_ids(students,query)
  
  for id in student_ids:
    scores = fetch_scores(id)
    print_scores(assns,id,scores)

def print_scores(assns,id,scores):
  for item in scores: 
    assn_id = item['problemSubmissionAssignmentId']
    score = item['problemSubmissionCredit']
    prob_id = item['problemSubmissionIdent']
    late = item['problemSubmissionLateCredit']
    time = item['problemSubmissionTime']
    print (assn_id,prob_id,score,late,time)

def get_documents(docs, args):
  if len(args) == 0: 
    print_help()

  for arg in args:
    if os.path.isfile(arg):
      print(f"{arg} already exists. Won't overwrite it.")
    else:
      first = True
      for item in docs:
        #if arg == item['filename']:
        if re.match(arg, item['filename']):
          first = throttle(first) 
          print(f"Fetching {item['filename']}")
          d = get_file(item['id'])
          file = open(item['filename'], 'w')
          file.write(d)
          file.close()

def put_documents(docs, args):
  if len(args) == 0:
    print_help()

  first = True
  for arg in args:
    if not os.path.isfile(arg):
      print(f"{arg} does not exist.")
    else:
      i = get_file_id(docs,arg)
      overwrite = False
      if i is None:
        first = throttle(first)
        params = {
          "filename": arg,
        }
        i = create_remote_document(params)
        overwrite = True
      # else:
      #   print(f'{arg} already exists on server.')
      #   print('Overwrite? [y/n]')
      #   reply = readchar.readchar()
      #   if reply in {'y', 'Y'}:
      #     overwrite = True

      overwrite = True
      if overwrite:
        file = open(arg,'r')
        content = file.read()
        file.close()
        first = throttle(first)
        print(f'Uploading {arg}')
        upload_document(i,content)
      else:
        print(f'Skipping {arg}')

def put_documents_new(docs, args):

  # Use capital letter options to apply to all documents
  filename = None
  scope = None
  description = None

  while True:
    if len(args) == 0:
      print_help()

    elif args[0] in {'-D', '--Description'}:
      if len(args) < 2:
        print_help()
      description = args[1]
      args = args[2:]

    elif args[0] in {'-S', '--Scope'}:
      if len(args) < 2:
        print_help()
      scope = args[1]
      #Private, Public, LinkOnly or InstructorsOnly
      args = args[2:]

    else:
      break

  while len(args) != 0:
    params = {
      "filename": filename,
      "description": description,
      "scope": scope
    }

    if args[0] in {'-d', '--description'}:
      if len(args) < 2:
        print_help()
      params['description'] = args[1]
      args = args[2:]

    if args[0] in {'-s', '--scope'}:
      if len(args) < 2:
        print_help()
      s = args[1]
      if s[:2] in { 'Pr', 'pr' }:
        params['scope'] = "Private"
      elif s[:2] in { 'Pu', 'pu' }:
        params['scope'] = "Public"
      elif s[:2] in { 'Li', 'li' }:
        params['scope'] = "LinkOnly"
      elif s[:2] in { 'In', 'in' }:
        params['scope'] = "InstructorsOnly"
      else:
        print(f'Scope not valid: {s}')
        raise SystemExit

      args = args[2:]

    if len(args) == 0:
      print_help()

    arg = args[0]
    params['filename'] = arg
    doc_id = get_file_id(docs,arg)
    if doc_id is None:
       doc_id = create_remote_document(params)
    else:
       doc = get_doc_by_id(docs,doc_id)
       if not params['description']:
         params['description'] = doc['description']
       if not params['scope']:
         params['scope'] = doc['scope']

    file = open(arg, 'r')
    content = file.read()
    file.close()
    print(f'Uploading {arg}')
    update_document(doc_id, params)
    upload_document(doc_id,content)
    
    args = args[1:]



def assn_documents(docs, assns, args):

  # Use capital letter options to apply to all assignments

  description = None
  points = None
  availability = None

  while True:
    if len(args) == 0:
      print_help()

    elif args[0] in {'-D', '--Description'}:
      if len(args) < 2:
        print_help()
      description = args[1]
      args = args[2:]

    elif args[0] in {'-T', '--Points'}:
      if len(args) < 2:
        print_help()
      points = int(args[1])
      args = args[2:]

    elif args[0] in {'-P', '--Password'}:
      if len(args) < 2:
        print_help()
      availability = {
        'tag': "HiddenViaPassword",
        'contents': str(args[1])
      }
      args = args[2:]
    else:
      break

  while len(args) != 0:
    params = {
      "document": None,
      "title": None,
      "description": description,
      "pointValue": points,
      "availability": availability, 
    }

    if args[0] in {'-d', '--description'}:
      if len(args) < 2:
        print_help()
      params['description'] = args[1]
      args = args[2:]

    if args[0] in {'-t', '--points'}:
      if len(args) < 2:
        print_help()
      params['pointValue'] = int(args[1])
      args = args[2:]

    if args[0] in {'-p', '--password'}:
      if len(args) < 2:
        print_help()
      params['availability'] = {
        'tag': "HiddenViaPassword",
        'contents': str(args[1])
      }
      args = args[2:]

    if len(args) == 0:
      print_help()

    params['title'] = args[0]
    params['document'] = get_file_id(docs,args[0])
    if params['document'] is None:
      print(f'{params["title"]} not found on server')
    else:
      assn = get_assn_by_title(assns,params['title'])
      if assn:
        if not params['description']:
          params['description'] = assn['description']
        if params['pointValue'] is None:
          params['pointValue'] = assn['pointValue']
        if not params['availability']:
          params['availability'] = assn['availability']
        patch_assignment(assn['id'],params)
      else:
        assign_document(params)

    args = args[1:]


def open_documents(docs, args):
  if len(args) == 0:
    print_help()

  for arg in args:
    i = get_file_id(docs,arg)
    if i is None:
      print(f'{arg} not found on server')
    else:
      url = f'{server}/shared/{instructor}/{arg}'
      webbrowser.open(url)

def print_help():
  print(__doc__.rstrip())
  raise SystemExit()

def main(args=sys.argv):
  
  args = args[1:]

  if len(args) == 0 or args[0] in {'-h', '--help', 'help'}:
    print_help()
  
  # commands that don't require server metadata

  if args[0] in {'manage'}:
    if len(args) == 1:
      webbrowser.open(f'{server}/instructor/{instructor}')
    elif args[1] == 'assns':
      webbrowser.open(f'{server}/instructor/{instructor}#assignFromDocument')
    elif args[1] == 'docs':
      webbrowser.open(f'{server}/instructor/{instructor}#uploadDocument')
    elif args[1] == 'course':
      webbrowser.open(f'{server}/instructor/{instructor}#course-1')
    elif args[1] == 'courses':
      webbrowser.open(f'{server}/instructor/{instructor}#manageCourse')
    else:
      print_help()
    raise SystemExit

  # commands that require server metadata
  
  docs = get_metadata()

  if args[0] in {'ls', 'list'}:
    args = args[1:]
    list_documents(docs, args)
    raise SystemExit
  elif args[0] in {'get', 'fetch'}:
    args = args[1:]
    get_documents(docs, args)
    raise SystemExit
  elif args[0] in {'put', 'push'}:
    args = args[1:]
    put_documents(docs, args)
    raise SystemExit
  elif args[0] in {'nput', 'npush'}:
    args = args[1:]
    put_documents_new(docs, args)
    raise SystemExit

  elif args[0] in {'open'}:
    args = args[1:]
    open_documents(docs, args)
    raise SystemExit

  # commands that require assignment metadata too

  assns = get_assignments()

  if args[0] in {'assns'}:
    list_assignments(assns)
    raise SystemExit
  elif args[0] in {'assn'}:
    args = args[1:]
    assn_documents(docs, assns, args)
    raise SystemExit
  elif args[0] in {'hiddens'}:
    list_hiddens(assns)
    raise SystemExit

  # commands that require student data too

  students = get_students()

  if args[0] in {'students'}:
    list_students(students)
    raise SystemExit
  elif args[0] in {'scores'}:
    args = args[1:]
    get_scores(students,assns,args)
    raise SystemExit
  elif args[0] in {'attempts'}:
    args = args[1:]
    list_attempts(students,assns,args)
    raise SystemExit

  print_help()

if __name__ == '__main__':
  #logging.basicConfig(filename='carnap.py.log',level=logging.DEBUG)
  #logging.basicConfig(filename='carnap.py.log',level=logging.WARNING)
  main()
