#!/usr/bin/env python
import Checkvist

emailusername=''
emailpassword=''
emailserver='imap.gmail.com'
emailfolder='INBOX'
checkvistlogin=''
checkvistapikey=''
checklistnumber=0


def email_to_checkvist(username,password,server,mailbox,cvusername,apikey,checklist):
	import imaplib,re

	# Connect to mail server
	i=imaplib.IMAP4_SSL(server)
	i.login(username,password)
	i.select(mailbox)
	counter=0

	# Connect to Checkvist
	c=Checkvist.Checkvist()
	c.authenticate(cvusername,apikey)

	# Get all unread mail
	typ,data=i.search(None,'UNSEEN')
	for num in data[0].split():
		# For each mail, get the body part
		typ, data = i.fetch(num, '(BODY[TEXT])')
		tasks = data[0][1].split('\n')

		# Mark the mail as read
		i.store(num, '+FLAGS', '\\Seen')

		# Add task for each line in mail up to '--'
		for t in tasks:
			if t.startswith('--'): break
			c.create_task(checklist,t.strip())
			counter=counter+1
	return counter

n=email_to_checkvist(emailusername,emailpassword,emailserver,emailfolder,checkvistlogin,checkvistapikey,checklistnumber)
if n>0: print "%d items added"%n
