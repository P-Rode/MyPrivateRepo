#!/bin/bash -x

# http://askubuntu.com/questions/355823/sending-file-using-sendmail

file=/path/to/file

mailalert(){
sendmail -F Sender-Name -it <<END_MESSAGE
To: Recipient@example.com
Subject: Subject

$(cat $file)
END_MESSAGE
}

mailalert_simple(){
uuencode /path/filename.txt
sendmail -F Sender-Name -it <<END_MESSAGE
To: per.rodenvall@gmail.com
Subject: Subject

Message
END_MESSAGE
}

sendmail -v user@domainname < test.mail

mailalert_simple

