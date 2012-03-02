import poplib
import socket

from subprocess import Popen, PIPE

from engine.config import Config


config = Config()
password = config.get('email', 'password')

handle_mail="/var/www/mailcheck/engine/handle_mail.py"
handle_mail_args="-ihotmail"
output=""

M = None
try:
  M=poplib.POP3_SSL("pop3.live.com", "995")
except socket.error:
  sys.exit(1)
except socket.timeout:
  sys.exit(1)
M.user("mcsmtp25@hotmail.com")
M.pass_(password)

numMessages = len(M.list()[1])
for i in range(numMessages):
  p=Popen([handle_mail, handle_mail_args], stdin=PIPE, close_fds=True)
  for j in M.retr(i+1)[1]:
    output += j+"\n"
  p.stdin.write(output);
  p.stdin.close();
  M.dele(i+1)
M.quit()

