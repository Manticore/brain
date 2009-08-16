"""
XML RPC client and server for database
They use not exactly standard XML RPC, but slightly extended one;
see xmlrpchelpers.py for details
"""

import threading
import random
import string
import inspect

import sys, os.path
scriptdir, scriptfile = os.path.split(sys.argv[0])
sys.path.append(os.path.join(scriptdir, ".."))

import brain
from brain import FacadeError, FormatError, LogicError, StructureError
from brain.xmlrpchelpers import MyXMLRPCServer, MyServerProxy, MyMultiCall

class BrainXMLRPCError(brain.BrainError):
	"""Signals an error in XML RPC layer"""
	pass

# methods, calls to which will be forwared to connection object
_CONNECTION_METHODS = ['create', 'modify', 'read', 'delete', 'insert',
	'readMany', 'insertMany', 'deleteMany', 'objectExists', 'search',
	'begin', 'beginSync', 'commit', 'rollback', 'dump', 'repair']


class _Dispatcher:
	"""Handles remote calls on server side, creates sessions and connection objects"""

	def __init__(self, db_path=None):
		self._sessions = {}
		self._db_path = db_path
		random.seed()

	def _dispatch(self, method, *args, **kwds):
		"""Handle remote call; pass it to this object or to connection object"""

		if method in _CONNECTION_METHODS:
			return self._dispatch_connection_method(method, *args, **kwds)

		try:
			func = getattr(self, 'export_' + method)
		except AttributeError:
			raise BrainXMLRPCError('method ' + method + ' is not supported')
		else:
			return func(*args, **kwds)

	def _dispatch_connection_method(self, method, session_id, *args, **kwds):
		"""Pass connection method to corresponding session"""

		if not isinstance(session_id, str):
			raise BrainXMLRPCError("Session ID must be string")

		if session_id not in self._sessions:
			raise BrainXMLRPCError("Session " + str(session_id) + " does not exist")

		func = getattr(self._sessions[session_id], method)
		return func(*args, **kwds)

	def export_connect(self, *args, **kwds):
		session_id = "".join(random.sample(string.ascii_letters + string.digits, 8))
		if self._db_path is not None:
			kwds['db_path'] = self._db_path
		self._sessions[session_id] = brain.connect(*args, **kwds)
		return session_id

	def export_close(self, session_id):
		self._sessions[session_id].close()
		del self._sessions[session_id]

	def export_getEngineTags(self):
		return brain.getEngineTags()

	def export_getDefaultEngineTag(self):
		return brain.getDefaultEngineTag()

	def _listMethods(self):
		return _CONNECTION_METHODS + ['close', 'getEngineTags', 'getDefaultEngineTag']

	def _findFunction(self, method_name):
		func = None
		if method_name in _CONNECTION_METHODS + ['close']:
			func = getattr(brain.connection.Connection, method_name)
		elif method_name == 'connect':
			func = brain.connect
		elif method_name in ['getEngineTags', 'getDefaultEngineTag']:
			func = getattr(brain.engine, method_name)
		return func

	def _methodHelp(self, method_name):
		func = self._findFunction(method_name)

		if func is None:
			return None

		return func.__doc__

	def _get_method_argstring(self, method_name):
		func = self._findFunction(method_name)

		if func is None:
			return None

		print(func)
		return inspect.formatargspec(inspect.getargspec(func))


class BrainServer:
	"""Class for brain DB server"""

	def __init__(self, port=8000, name=None, db_path=None):

		# server thread name
		if name is None:
			name = "Brain XML RPC server on port " + str(port)

		self._server = MyXMLRPCServer(("localhost", port))
		self._server.allow_reuse_address = True
		self._server.register_instance(_Dispatcher(db_path=db_path))
		self._server_thread = threading.Thread(name=name,
			target=self._server.serve_forever)

	def start(self):
		"""Start server"""
		self._server_thread.start()

	def stop(self):
		"""Stop server and wait for it to finish"""
		self._server.shutdown()
		self._server_thread.join()


class BrainClient:
	"""Class for brain DB client"""

	def __init__(self, addr):
		self._client = MyServerProxy(addr, exceptions=[FacadeError,
			FormatError, LogicError, StructureError, BrainXMLRPCError])

	def getEngineTags(self):
		return self._client.getEngineTags()

	def getDefaultEngineTag(self):
		return self._client.getDefaultEngineTag()

	def connect(self, *args, **kwds):
		return _RemoteConnection(self._client, *args, **kwds)


class _RemoteConnection:
	"""Class which mimics local DB connection"""

	def __init__(self, client, *args, **kwds):
		self._client = client
		self._session_id = client.connect(*args, **kwds)
		self._multicall = None
		self._transaction = False

	def __getattr__(self, name):
		# close() will be called for connection object, but it should be passed to
		# dispatcher, because it has to delete corresponding session after
		# closing it
		if name not in _CONNECTION_METHODS + ['close']:
			raise AttributeError("Cannot find method " + str(name))

		# Pass method call to server, adding session ID to it
		def wrapper_session(*args, **kwds):
			return method(self._session_id, *args, **kwds)

		if self._multicall is not None:
			method = getattr(self._multicall, name)
			return method
		else:
			method = getattr(self._client, name)
			return wrapper_session

	def beginSync(self):
		if self._transaction:
			raise FacadeError("Transaction is already in progress")

		self.__getattr__('beginSync')()
		self._transaction = True

	def begin(self):
		if self._transaction:
			raise FacadeError("Transaction is already in progress")

		self._multicall = MyMultiCall(self._client, self._session_id)
		self._multicall.begin()
		self._transaction = True

	def rollback(self):
		if not self._transaction:
			raise FacadeError("Transaction is not in progress")

		self._transaction = False
		if self._multicall is None:
			self.__getattr__('rollback')()
		else:
			self._multicall = None

	def commit(self):
		if not self._transaction:
			raise FacadeError("Transaction is not in progress")
		self._transaction = False

		if self._multicall is None:
			return self.__getattr__('commit')()
		else:
			try:
				self._multicall.commit()
				res = list(self._multicall())
				return res[-1]
			finally:
				self._multicall = None
