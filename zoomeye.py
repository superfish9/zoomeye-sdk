import json
import requests
import urllib

class ZoomeyeError(Exception):
	'''
	Errors.
	'''
	def __init__(self, status_code, content):
		self.status_code = status_code
		self.error = json.loads(content)['error']
		self.message = json.loads(content)['message']
		self.url = json.loads(content)['url']

	def print_error(self):
		'''
		Print error info.
		'''
		print 'status_code: %d' % self.status_code
		print 'error: %s' % self.error
		print 'message: %s' % self.message
		print 'url: %s' % self.url

class ZoomeyeResult(object):
	'''
	Make result a class
	'''
	def __init__(self, result):
		result = json.loads(result)
		if result.has_key('plan'):
			self.plan = result['plan']
		if result.has_key('resources'):
			self.resources = result['resources']
		if result.has_key('matches'):
			self.matches = result['matches']
		if result.has_key('facets'):
			self.facets = result['facets']
		if result.has_key('total'):
			self.total = result['total']

class zoomeye(object):
	'''
	Zoomeye api. Init with username and password.
	'''
	def __init__(self, username, password):
		self.baseurl = 'http://api.zoomeye.org/'
		self.username = username
		self.password = password
		self.s = requests.Session()
		self.headers = {}
		self.authdata = '{ "username": "' + username + '", "password": "' + password + '" }'

		try:
			resp = self.s.post(url=self.baseurl + 'user/login', data=self.authdata)
			if resp.status_code not in (200, 201):
				raise ZoomeyeError(resp.status_code, resp.content)
			self.token = json.loads(resp.content)['access_token']
			self.headers['Authorization'] = 'JWT ' + self.token
		except ZoomeyeError as e:
			e.print_error()
			exit(-1)

	def _handle_query(self, query):
		'''
		Make query from dict to string.
		'''
		if isinstance(query, dict):
			query_dict = query
			query = ''
			for key in query_dict:
				query += str(key) + ':' + str(query_dict[key]) + ' '
			return query[:-1]
		else:
			return str(query)

	def resources_info(self):
		'''
		Resources info.
		'''
		url = self.baseurl + 'resources-info'

		try:
			resp = self.s.get(url=url, headers=self.headers)
			if resp.status_code not in (200, 201):
				raise ZoomeyeError(resp.status_code, resp.content)
		except ZoomeyeError as e:
			e.print_error()
			exit(-1)

		return ZoomeyeResult(resp.content)

	def search(self, query, page=1, facets=[], t='host'):
		'''
		Search the host devices or Web technologies.
		'''
		query = urllib.quote('"' + self._handle_query(query) + '"')
		page = urllib.quote(str(page))
		facets = urllib.quote(str(facets)[1:-1])
		if t not in ('host', 'web'):
			t = 'host'

		try:
			resp = self.s.get(url=self.baseurl + '%s/search?query=%s&page=%s&facet=%s' % (t, query, page, facets), headers=self.headers)
			if resp.status_code not in (200, 201):
				raise ZoomeyeError(resp.status_code, resp.content)
		except ZoomeyeError as e:
			e.print_error()
			exit(-1)

		return ZoomeyeResult(resp.content)
