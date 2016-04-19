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
	Make result a class.
	'''
	def __init__(self, result):
		self.plan = ''
		self.resources = ''
		self.matches = ''
		self.facets = ''
		self.total = ''

		result = json.loads(result)
		if result.has_key('plan'):
			self.plan = result['plan']
		if result.has_key('resources'):
			self.resources = result['resources']
		if result.has_key('matches'):
			self.matches = result['matches']
			self.result_len = len(self.matches)
		if result.has_key('facets'):
			self.facets = result['facets']
		if result.has_key('total'):
			self.total = result['total']

	def get_ip_list(self, num=0):
		'''
		Get ip list from result. Only for host search.
		'''
		if not self.matches or not isinstance(self.matches[0]['ip'], basestring):
			return []

		ip_list = []
		if num <= 0 or num >= self.result_len:
			ip_num = self.result_len
		else:
			ip_num = num
		for i in range(0, ip_num):
			ip_list.append(self.matches[i]['ip'])
		return ip_list

	def get_portinfo_list(self, ip=[]):
		'''
		Get portinfo list (of some ip) from result. Only for host search.
		'''
		if not self.matches or not self.matches[0].has_key('portinfo'):
			return {}

		portinfo_list = {}
		if isinstance(ip, basestring):
			ip_list = ip
		elif ip == []:
			ip_list = self.get_ip_list()
		else:
			ip_list = ip
		for i in range(0, self.result_len):
			if self.matches[i]['ip'] in ip_list:
				portinfo_list[self.matches[i]['ip']] = self.matches[i]['portinfo']
		return portinfo_list

	def get_site_list(self, num=0):
		'''
		Get site list from result. Only for Web search.
		'''
		if not self.matches or not self.matches[0].has_key('site'):
			return []

		site_list = []
		if num <= 0 or num >= self.result_len:
			site_num = self.result_len
		else:
			site_num = num
		for i in range(0, site_num):
			site_list.append(self.matches[i]['site'])
		return site_list

	def get_webinfo_list(self, site=[]):
		'''
		Get webinfo list (of some site) from result. Only for Web search.
		'''
		if not self.matches or not self.matches[0].has_key('site'):
			return {}

		webinfo_list = {}
		if isinstance(site, basestring):
			site_list = site
		elif site == []:
			site_list = self.get_site_list()
		else:
			site_list = site
		for i in range(0, self.result_len):
			if self.matches[i]['site'] in site_list:
				webinfo_list[self.matches[i]['site']] = {}
				webinfo_list[self.matches[i]['site']]['db'] = self.matches[i]['db']
				webinfo_list[self.matches[i]['site']]['domains'] = self.matches[i]['domains']
				webinfo_list[self.matches[i]['site']]['language'] = self.matches[i]['language']
				webinfo_list[self.matches[i]['site']]['ip'] = self.matches[i]['ip']
				#webinfo_list[self.matches[i]['site']]['server'] = self.matches[i]['server']
				webinfo_list[self.matches[i]['site']]['webapp'] = self.matches[i]['webapp']
		return webinfo_list


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
