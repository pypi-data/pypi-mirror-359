from abc import ABC, abstractmethod
import typing as t

import functools
import re

from ..base import Checker, MultiConditionChecker, SingleConditionChecker



class CheckerBuilder(ABC):
	"""Checker builder
	
	Creates a checker from a raw data of any type.
	"""

	@abstractmethod
	def __call__(self, raw: t.Any) -> Checker:
		"""
		
		:param raw: A raw data to be converted into a checker
		:type raw: typing.Any

		:return: A checker
		:rtype: Checker
		"""
		pass



def getComparator(sample: t.Any, func: t.Callable[[
	t.Any,	# argument
	t.Any	# sample
], bool]):
	"""Comparator creating function

	Creates a singly-argumented function from a binary comparison
	function.

	:param sample: A value a parameter has to be compared with
	:type sample: typing.Any

	:param func: A binary comparison function
	:type func: typing.Callable[[typing.Any, typing.Any], bool]
	"""

	def comparator(value: t.Any) -> bool:
		return func(value, sample)
	return comparator



class MatchCondition:
	"""Match condition
	
	The regex-based functor returning `True` if given parameter matches a regex.
	"""

	def __init__(self, pattern: str) -> None:
		"""
		
		:param pattern: A regex pattern
		:type pattern: str
		"""
		self.__regex = re.compile(pattern)


	def __call__(self, s: str) -> bool:
		"""
		
		:param s: String to be validated
		:type s: str

		:return: `True` if the string matches, `False` otherwise
		"""
		matchResult = self.__regex.match(s)
		return bool(matchResult)



class DefaultCheckerBuilder(CheckerBuilder):
	"""Default checker builder
	
	The checker builder which is used by default.
	"""

	CONDITION_BUILDER_MAPPING = {
		# binary comparison
		"lt": functools.partial(getComparator, func=lambda l, r: l < r), # Less Than
		"le": functools.partial(getComparator, func=lambda l, r: l <= r), # Less or Equal
		"gt": functools.partial(getComparator, func=lambda l, r: l > r), # Greater Than
		"ge": functools.partial(getComparator, func=lambda l, r: l >= r), # Greater or Equal
		"eq": functools.partial(getComparator, func=lambda l, r: l == r), # EQual
		"ne": functools.partial(getComparator, func=lambda l, r: l != r), # Not Equal

		# other
		"regex": MatchCondition # regular expression
	}
	"""Name-condition mapping;
	allows to evaluate such `JSON`: `{"param": {"lt": 5, "ge": 3}}`
	"""

	DEFAULT_CONDITION_BUILDER = CONDITION_BUILDER_MAPPING["eq"]
	"""The default condition builder;
	allows to evaluate such `JSON`:
	`{"param": 5}`, which is similar to `{"param": {"eq": 5}}`
	"""


	def __init__(self, paramName: str) -> None:
		"""
		
		:param paramName: Name of the parameter to be checker by a created checker
		:type paramName: str
		"""
		self.__paramName = paramName


	def __call__(self, raw: t.Any) -> Checker:
		"""
		
		:param raw: A `JSON` expression to be converted into a checker
		:type raw: typing.Any

		:return: A checker
		:rtype: Checker
		"""
		if isinstance(raw, t.Mapping):
			conditions = list(map(
				lambda item: DefaultCheckerBuilder.\
					CONDITION_BUILDER_MAPPING[item[0]](item[1]),
				raw.items()
			))
			return MultiConditionChecker(self.__paramName, conditions)

		condition = DefaultCheckerBuilder.DEFAULT_CONDITION_BUILDER(raw)
		return SingleConditionChecker(self.__paramName, condition)
