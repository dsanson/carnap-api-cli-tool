#!/usr/bin/env python3
"""\
Usage:
  carnap.py action [args]

Actions:
  ls: list all files on server 
  ls <regex>: with filenames matching [regex]
  get [files|regexes]: fetch [files] from server
  put [files]: upload [files] to server
  open [files|regexes]: open [files] on server in browser
  assn: open the Carnap assignment page in browser
  manage: open the Carnap upload page in browser
  course <number>: open the Carnap course page in browser
  help: show this help
"""

import requests
import logging
import sys
import re
import os.path
import time
import readchar
from pathlib import Path
import yaml
import webbrowser

# Load config file

dummy_apikey = '<apikey>'
dummy_instructor = 'rudolf@example.com'
default_server = 'http://localhost:3000'

config_template=f'''\
---
apikey: {dummy_apikey}
instructor: {dummy_instructor}
server: {default_server}
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

def create_remote_file(filename):
  return rq('POST', f'/instructors/{instructor}/documents',
      json={
        "filename": filename,
      }).json()

def upload_document(i,content):
  rq('PUT', f'/instructors/{instructor}/documents/{i}/data', 
      data=content.encode('utf-8'))

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

# Actions

def list_documents(docs, args):
  filter = True
  if len(args) == 0:
    filter = False

  for item in docs:
    if not filter or re.match(args[0], item['filename']):
      print(f"{item['id']}: {item['filename']}")
        

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
        i = create_remote_file(arg)
        overwrite = True
      else:
        print(f'{arg} already exists on server.')
        print('Overwrite? [y/n]')
        reply = readchar.readchar()
        if reply in {'y', 'Y'}:
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

def open_course_page(args):
  if len(args) == 0:
    course = 1
  else:
    course = args[0]
  webbrowser.open(f'{server}/instructor/{instructor}#course-{course}')

def print_help():
  print(__doc__.rstrip())
  raise SystemExit()

def main(args=sys.argv):
  
  args = args[1:]

  if len(args) == 0 or args[0] in {'-h', '--help', 'help'}:
    print_help()
  
  # commands that don't require server metadata

  if args[0] in {'assn'}:
    webbrowser.open(f'{server}/instructor/{instructor}#assignFromDocument')
    raise SystemExit
  elif args[0] in {'manage'}:
    webbrowser.open(f'{server}/instructor/{instructor}#uploadDocument')
    raise SystemExit
  elif args[0] in {'course'}:
    args = args[1:]
    open_course_page(args)
    raise SystemExit

  # commands that require server metadata
  
  docs = get_metadata()

  if args[0] in {'ls', 'list'}:
    args = args[1:]
    list_documents(docs, args)
  elif args[0] in {'get', 'fetch'}:
    args = args[1:]
    get_documents(docs, args)
  elif args[0] in {'put', 'push'}:
    args = args[1:]
    put_documents(docs, args)
  elif args[0] in {'open'}:
    args = args[1:]
    open_documents(docs, args)

if __name__ == '__main__':
  #logging.basicConfig(filename='carnap.py.log',level=logging.DEBUG)
  #logging.basicConfig(filename='carnap.py.log',level=logging.WARNING)
  main()
