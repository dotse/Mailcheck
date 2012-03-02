#!/usr/bin/env python
from sys import argv, stdin
import getopt

def usage():
  print "Usage: " + str(argv[0]) + " [options]"
  print "  options:"
  print "  -i <arg>\tor\t--in=<arg>\t\tfor incoming mail (ie. gmail, not postfix alias)"
  print ""
  exit()

incoming=False
in_source=None

if len(argv) > 1:
  try:
    opts, args = getopt.getopt(argv[1:], 'hi:', [ 'in=', 'help' ])
  except getopt.GetoptError, err:
    usage()
  for i in opts:
    opt, arg = i
    if opt == '--in' or opt == '-i':
      incoming=True
      in_source=arg
    elif opt == '--help' or opt == '-h':
      usage()
    else:
      exit()

import re
import socket
import smtplib
from subprocess import Popen, PIPE
from os import waitpid
import time
import dkim
from engine.database import *
from engine.config import Config

config = Config()
mailcheck_subject = ".*This is mailcheck.*"

try:
  db = Database()
  db.connect()
except DatabaseConnectionFailedException, e:
  print 'Could not establish connection with the database. Shutting down...'
  exit()

db_ip="127.0.0.1"
dir="/var/www/cache/"
file=str(time.time())
output=""
extra_tests=[]


def parse_mail():
  global dir, file, incoming, mailcheck_subject, extra_tests, in_source, in_save

  max_size=102400
  output="";
  size=0
  email=""
  domain=""
  unixtime=""
  testid=None
  body=False
  from_mailcheck=False
  match_test=False

  f=open(dir+file, "a+w")
  f.write(email + " " + domain + "\n")
  for line in stdin.readlines():
    f.write(line)
    # read stdin to string "output" and also calculate size
    size = + (len(line) + size);
    output += line;
    if (size >= max_size):
      exit("Max size exceeded")
    elif re.match("^Subject: ", line):
      if re.match(mailcheck_subject, line, re.I):
        from_mailcheck=True
    elif re.match("From: ", line):
      email_regexp=re.compile(r"^From:[^<]*([a-z,0-9,-,.<]*@[a-z,0-9,.,-]*\.[a-z]*).*$", re.IGNORECASE)
      email=str(re.sub(email_regexp, r"\1", line)).strip()
      email=email.strip("<>\"'[]")
      #domain=email.split("@")[1]
    elif re.match("^DKIM-Signature: ", line) and (body == False):
      extra_tests.append('DKIM')
    elif (body == False) and re.match(r"^Received:.*from [a-z,A-Z,0-9].*", line) and (domain == ""):
      #>>> line="        by svosch.gatorhole.com (Postfix) with ESMTPSA id 1276FBE57D;"
      domain=re.sub("[^from]*([a-z,0-9,-].*\.[a-z,A-Z]{1,3}).*", r"\1", line).split()[1]
      domain=domain.strip('\(')
      f.write("Body False, match by\n")
    elif (body == False) and re.match("^$", line):
      body=True
      f.write("Body False, match empty\n")
    elif (body == True) and re.match(r"[0-9]{10}-[0-9]*", line):
      unixtime_testid=re.sub(r".*([0-9]{10}-[0-9]{1,}).*", r"\1", line).split("-")
      f.write("Body True, content\n")
      unixtime=unixtime_testid[0]
      testid=unixtime_testid[1].split("\n")[0]
      if (from_mailcheck == True):
        match_test=email_match_test(testid, unixtime, email)
        match_queue=email_match_queue(testid, unixtime, email)
        if (incoming == True) and ((match_queue == True) or (match_test == True)): 
          if in_source == 'hotmail':
            message = 'Hotmail mail recieved.'
          elif in_source == 'gmail':
            message = 'Gmail mail recieved.'
          else:
            exit(in_source)
          save_result(testid, message, 1, 'adv', 'Webmail', 'Incoming', '0', '0', int())
          save_result(testid, message, 1, 'adv', 'Webmail', 'Incoming', '1', '0', int())
          in_save=True

  return [ output, email, domain , unixtime, testid, extra_tests ]


def email_match_test(testid, unixtime, email):
  query = "select COUNT(id) from test where id=%s and extract('epoch' from queued)::integer = %s and email=%s"
  print str(testid) + " : " + str(unixtime) + " : " + str(email)
  test=db.fetch(query, ( testid, unixtime, email ))
  if int(test[0][0]) != 0:
    return True
  else:
    return False

def email_match_queue(testid, unixtime, email):
  query = "select COUNT(id) from queue where test_id=%s and extract('epoch' from start_time)::integer = %s and email=%s"
  print str(testid) + " : " + str(unixtime) + " : " + str(email)
  queue=db.fetch(query, ( testid, unixtime, email ))
  if int(queue[0][0]) != 0:
    return True
  else:
    return False

def save_result(testid, message, status, type, plugin, category, final, goldstar, parent):
  #        INSERT INTO result (test_id, message, status, type, plugin, category, final, goldstar, parent ) VALUES (1067, 'Hotmail OK', 0, 'adv', 'Webmail', 'Incoming', 1, 0, 1066);
  #query = "INSERT INTO result (test_id, message, status, type, plugin, category, final, goldstar, parent ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s ) RETURNING id"

  sql = "INSERT INTO plugin (test_id, plugin, status, category) VALUES(%s,%s,%s,%s)"
  params = [testid, plugin, status, category]
  db.query(sql, params)

  query = "INSERT INTO plugin_result (test_id, plugin, name, value_text, table_id) VALUES(%s,%s,%s,%s,nextval('table_id_seq'::regclass)) RETURNING id"
  params = [testid, plugin, 'output_text', message]

  #result=db.fetch(query, (testid, message, status, type, plugin, category, final, goldstar, parent))
  result=db.fetch(query, params)



if incoming == True:
  in_save=False
  output, email, domain, unixtime, testid, extra_tests = parse_mail()
  if in_save==True:
    dir=str(dir) + "/incoming/"
    file=str(unixtime)+"-"+str(testid)
    f=open(dir+file, "a+w")
    f.write(str(output))
    server = smtplib.SMTP('localhost')
    server.sendmail("mailcheck@mailcheck.iis.se", email, "Subject: mailcheck resultat\n\nhttp://mailcheck.iis.se/result/"+str(unixtime)+"-"+str(testid))
    server.quit()
else:
  output, email, domain, unixtime, testid, extra_tests = parse_mail()
  f=open(dir+file, "a+w")
  if testid == None:
    query = "INSERT INTO queue (domain, email, test_id, ip, extra) VALUES(%s, %s, nextval('test_id_seq'), %s, 'StartTLS;SPF') RETURNING test_id, EXTRACT(EPOCH FROM start_time)::integer AS start_time"
    test=db.fetch(query, ( domain, email, db_ip ))
    f.write( query + str(test) + str(unixtime) + str(domain) + str(email) + "\n")
  else:
    params = ( testid, unixtime )
    query="SELECT count(id), start_time FROM queue WHERE test_id=%s AND EXTRACT(EPOCH FROM start_time)::integer = %s GROUP BY start_time"
    test = db.fetch(query, params)
    if len(test) <= 0:
      query="SELECT count(id), queued FROM test WHERE id=%s AND EXTRACT(EPOCH FROM queued)::integer = %s GROUP BY queued"
      test=db.fetch(query, params)

    f.write( query + str(testid) + str(unixtime) + "\n")
    f.write( str(test) + "\n")
    if (len(test) >= 1) and int(test[0][0]) == 1:
      timestamp=test[0][1]
      parent = testid
      query = "INSERT INTO queue (domain, email, test_id, parent, start_time, ip, extra, slow) VALUES(%s, %s, nextval('test_id_seq'), %s, %s, %s, 'd:StandardAddresses', true) RETURNING test_id, EXTRACT(EPOCH FROM start_time)::integer AS start_time"
      test=db.fetch(query, ( domain, email, testid, timestamp, db_ip ))
      testid = test[0][0]

      f.write(str(test)+"\n")
    else:
      exit(str("No matching test"))
  f.write(str(output)+"\n"+str(query)+"\n")


if len(extra_tests) >= 1:
  for extra in extra_tests:
    if extra == 'DKIM' and incoming == False:
      dkim=dkim.verify(output)
      if dkim == True:
        message='DKIM test successful'
        goldstar='1'
        status='1'
      else:
        message='DKIM-test failed'
        goldstar='0'
        status='2'
      save_result(testid, message, status, 'adv', 'DKIM', 'Incoming', '0', goldstar, int())
      save_result(testid, message, status, 'adv', 'DKIM', 'Incoming', '1', goldstar, int())
