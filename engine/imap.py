#!/usr/bin/env python
import imaplib
from os import waitpid
from subprocess import Popen, PIPE
from re import sub

from engine.config import Config

config = Config()
password = config.get('email', 'password')

python="/usr/bin/python"
handle_mail="/var/www/mailcheck/engine/handle_mail.py"
handle_mail_args="-igmail"

i = imaplib.IMAP4_SSL("imap.gmail.com")
i.login("mcsmtp25@gmail.com", password)
i.select()
typ, data = i.search(None, 'ALL')
for num in data[0].split():
  p=Popen([handle_mail, handle_mail_args], stdin=PIPE, close_fds=True)
  typ, data = i.fetch(num, '(RFC822)')
  output=sub(r'\r', '', data[0][1])
  p.stdin.write(output);
  i.store(num, '+FLAGS', '\\Deleted')
  p.stdin.close();
  
i.close()
i.logout()

