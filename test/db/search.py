"""Unit tests for database layer search request"""

import sys, os.path
scriptdir, scriptfile = os.path.split(sys.argv[0])
sys.path.append(os.path.join(scriptdir, ".."))

import unittest
from test import helpers
from test.db.requests import TestRequest
from db.database import *
from db.interface import *

class Search(TestRequest):
	"""Test operation of SearchRequest"""

	def testConditionAnd(self):
		"""Check complex condition with And operator"""
		self.prepareStandNoList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Eq(), '1111'
			),
		SearchRequest.And(),
		SearchRequest.Condition(
			Field('age'), SearchRequest.Eq(), '22'
			)
		)))

		self.checkRequestResult(res, ['5'])

	def testConditionOr(self):
		"""Check complex condition with Or operator"""
		self.prepareStandNoList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Eq(), '2222'
			),
		SearchRequest.Or(),
		SearchRequest.Condition(
			Field('age'), SearchRequest.Eq(), '27'
			)
		)))

		self.checkRequestResult(res, ['2', '3'])

	def testConditionInvert(self):
		"""Check operation of inversion flag in condition"""
		self.prepareStandNoList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Eq(), '1111'
			),
		SearchRequest.And(),
		SearchRequest.Condition(
			Field('age'), SearchRequest.Eq(), '22', invert=True
			)
		)))

		self.checkRequestResult(res, ['1'])

	def testConditionInvertInRoot(self):
		"""Check if inversion flag works in the root of condition"""
		self.prepareStandNoList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Eq(), '1111'
			),
		SearchRequest.And(),
		SearchRequest.Condition(
			Field('age'), SearchRequest.Eq(), '22', invert=True
			),
		invert=True
		)))

		self.checkRequestResult(res, ['2', '3', '4', '5'])

	def testConditionRegexp(self):
		"""Check operation of regexp-based condition"""
		self.prepareStandNoList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Regexp(), '\d+'
			),
		SearchRequest.And(),
		SearchRequest.Condition(
			Field('age'), SearchRequest.Eq(), '22', invert=True
			)
		)))

		self.checkRequestResult(res, ['1', '2', '3', '4'])

	def testConditionRegexpOnPart(self):
		"""Regression for bug when there was match() instead of search() in regexp callback"""
		self.prepareStandNoList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
			Field('name'), SearchRequest.Regexp(), 'ex'
			)))

		self.checkRequestResult(res, ['1', '5'])

	def testNonExistentFieldInAndCondition(self):
		"""Check that condition on non-existent field works with And operator"""
		self.prepareStandNoList()

		# Second part of the condition should return empty list,
		# so the whole result should be empty too
		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Eq(), '1111'
			),
		SearchRequest.And(),
		SearchRequest.Condition(
			Field('blablabla'), SearchRequest.Eq(), '22', invert=True
			)
		)))

		self.checkRequestResult(res, [])

	def testNonExistentFieldInOrCondition(self):
		"""Check that condition on non-existent field works with Or operator"""
		self.prepareStandNoList()

		# Second part of the condition should return empty list,
		# so the whole result should be equal to the result of the first part
		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field('phone'), SearchRequest.Eq(), '1111'
			),
		SearchRequest.Or(),
		SearchRequest.Condition(
			Field('blablabla'), SearchRequest.Eq(), '22', invert=True
			)
		)))

		self.checkRequestResult(res, ['1', '5'])

	def testListOneLevel(self):
		"""Check searching in simple lists"""
		self.prepareStandSimpleList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
			Field(['tracks', None]), SearchRequest.Eq(), 'Track 2'
			)))

		self.checkRequestResult(res, ['1', '2'])

	def testListOneLevelDefinedPosition(self):
		"""Check search when some of positions in lists are defined"""
		self.prepareStandSimpleList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
			Field(['tracks', 1]), SearchRequest.Eq(), 'Track 2'
			)))

		self.checkRequestResult(res, ['1'])

	def testNestedList(self):
		"""Check searching in nested lists"""
		self.prepareStandNestedList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
			Field(['tracks', 0, 'Authors', None]), SearchRequest.Eq(), 'Alex'
			)))

		self.checkRequestResult(res, ['1'])

	def testNestedListRegexp(self):
		"""Check regexp searching in nested lists"""
		self.prepareStandNestedList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
			Field(['tracks', 1, 'Authors', None]), SearchRequest.Regexp(), 'Carl'
			)))

		self.checkRequestResult(res, ['1'])

	def testNestedListComplexCondition(self):
		"""Check search in nested list with complex condition"""
		self.prepareStandNestedList()

		res = self.db.processRequest(SearchRequest(SearchRequest.Condition(
		SearchRequest.Condition(
			Field(['tracks', None]), SearchRequest.Eq(), 'Track 11'
			),
		SearchRequest.And(),
		SearchRequest.Condition(
			Field(['tracks', None, 'Name']), SearchRequest.Regexp(), 'name'
			)
		)))

		self.checkRequestResult(res, ['2'])

def get_class():
	return Search