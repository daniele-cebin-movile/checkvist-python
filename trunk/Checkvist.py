import urllib2
class CheckvistError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class AuthenticationFailure(CheckvistError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class RequestWithMethod(urllib2.Request):
  def __init__(self, method, *args, **kwargs):
    self._method = method
    urllib2.Request.__init__(self,*args, **kwargs)

  def get_method(self):
    return self._method

class Checkvist(object):
	"""A simple class for interfacing with the Checkvist open API."""
	token=None

	def authenticate(self,username,apikey):
		"""Authenticate with the API. Returns a string containing the authentication token, which will also be automatically
		sent with any following API requests.

		On failure, will raise an AuthenticationFailure."""

		# Attempt to obtain a login token
		token=self._req('/auth/login.json', {'username': username, 'remote_key': apikey}, True)

		# Check that the response is a string; if so, store it and return it
		if (type(token)==unicode):
			self.token=token
			return token
		else:
			raise CheckvistError("Unexpected response on authenticate!")

	def de_authenticate(self):
		"""Discard the current authentication token and go back to anonymous mode."""
		self.token=None

	def get_lists(self):
		"""Returns a list of all the current user's lists."""
		return self._req('/checklists.json')

	def create_list(self,name=''):
		"""Creates a new checklist, optionally with the supplied name."""
		return self._req('/checklists.json', {'checklist[name]': name}, True)

	def get_list_info(self, checklist):
		"""Returns a dict containing the attributes of the specified list."""
		return self._req('/checklists/%d.json' % checklist)

	def get_tasks(self,checklist,with_notes=False):
		"""Returns a list of tasks for the specified list."""
		if (with_notes):
			return self._req('/checklists/%d/tasks.json' % checklist, {'with_notes': 1})
		else:
			return self._req('/checklists/%d/tasks.json' % checklist)

	def get_task(self,checklist,task,with_notes=False):
		"""Returns a list containing the given task and its parents."""
		if (with_notes):
			return self._req('/checklists/%d/tasks/%d.json' % (checklist,task), {'with_notes': 1})
		else:
			return self._req('/checklists/%d/tasks/%d.json' % (checklist,task))


	def create_task(self,checklist,content,position=None,status=0,parent_id=None):
		"""Create a new task; returns a dict representation of if."""
		args={'task[content]': content, 'task[status]': status}
		if (position!=None): args['task[position]']=position
		if (parent_id!=None): args['task[parent_id]']=parent_id
		return self._req('/checklists/%d/tasks.json' % checklist, args, True)

	def import_tasks(self,checklist,import_content):
		"""Import the given content into the specified checklist."""
		return self._req('/checklists/%d/import.json' % checklist, {'import_content': import_content}, True)

	def update_task(self,checklist,task,content=None, position=None, parent_id=None):
		"""Update the specified task, changing any of: content, position or parent_id"""

		if (content==position==parentid==None): return False
		args={}
		if (content!=None): args['task[content]']=content
		if (position!=None): args['task[position]']=position
		if (parent_id!=None): args['task[parent_id]']=parent_id
		return self._req('/checklists/%d/tasks/%d.json' % checklist, args, True)

	def close_task(self,checklist,task):
		return self._req('/checklists/%d/tasks/%d/close.json' % (checklist, task), {}, True)

	def open_task(self,checklist,task):
		return self._req('/checklists/%d/tasks/%d/open.json' % (checklist, task), {}, True)

	def invalidate_task(self,checklist,task):
		return self._req('/checklists/%d/tasks/%d/invalidate.json' % (checklist, task), {}, True)


	def change_task_status(self, checklist, task, status):
		"""Change the status of the given task to 0 (open), 1 (closed) or 2 (invalidated)"""
		if (status==0): return self.open_task(checklist, task)
		elif (status==1): return self.close_task(checklist, task)
		elif (status==2): return self.invalidate_task(checklist, task)
	
	def delete_task(self, checklist, task):
		self._req('/checklists/%d/tasks/%d.json' % (checklist, task), {}, False, True)

	def _req(self,url,values={}, post=False, delete=False):
		import urllib2, urllib, json
		url = 'http://checkvist.com'+url
		postvars=values.copy()

		if (self.token): postvars['token']=self.token
		#postvars.update(token=self.token)

		if (delete):
			req=RequestWithMethod('DELETE', url+"?"+urllib.urlencode(postvars))
		elif (post):
			req=urllib2.Request(url,urllib.urlencode(postvars))
		else:
			req=urllib2.Request(url+"?"+urllib.urlencode(postvars))

		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError as e:
			if (e.getcode()==401):
				raise AuthenticationFailure("Invalid credentials supplied")
			pass
		else:
			try:
				data = json.loads(response.read())
			except ValueError:
				return None
			else:
				return data

