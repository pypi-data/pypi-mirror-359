from abc import ABC, abstractmethod
import typing as t
from .checker import Estimand, Checker



Estimation = t.TypeVar("Estimation")
"""The estimation generic type"""



class Criterion(ABC, t.Generic[Estimation]):
	"""The criterion base class
	
	Criteria are used to convert estimand into an estimation
	(just a generic single-argument generic functor).
	"""

	@abstractmethod
	def __call__(self, estimand: Estimand) -> Estimation:
		"""
		
		Converts an estimand into an estimation.

		:param estimand: A value to be estimated
		:type estimand: Estimand

		:return: An estimation
		:rtype: Estimation
		"""
		pass



class BasicCriterion(Criterion[Estimation]):
	"""The basic criterion implementation
	
	Consider that the CriterionImpl class if you feel it more comfortable.
	Uses checkers (single-argument boolean functors).
	"""

	def __init__(
		self,
		estimation: Estimation,
		checkers: t.Iterable[Checker] = []
	) -> None:
		"""

		:param estimation: An estimation to be returned on the successful assertion
		:type estimation: Estimation

		:param checkers: Checkers to be executed for the assertion; default is `[]`
		:type checkers: typing.Iterable[Checker]
		"""
		self.estimation = estimation
		self.checkers = checkers


	def __call__(self, estimand: Estimand) -> Estimation:
		"""
		
		Returns the estimation if all the checkers return True.
		Otherwise throws the AssertionError.

		:param estimand: A value to be estimated
		:type estimand: Estimand

		:return: An estimation
		:rtype: Estimation

		:raises AssertionError: At least one checker has failed
		"""
		assert all(checker(estimand) for checker in self.checkers)
		return self.estimation



class ValidatingCriterion(Criterion[Estimation]):
	"""Validating criterion class

	Supposed to validate an estimand before estimating.
	"""

	def __init__(
		self,
		criterion: Criterion[Estimation],
		validator: t.Callable[[Estimand], None]
	) -> None:
		"""
		
		:param criterion: A criterion to be checker after the validation
		:type criterion: Criterion[Estimation]

		:param validator: A function throwing an exception if an estimand is invalid
		:type validator: typing.Callable[[Estimand], None]
		"""
		self.__criterion = criterion
		self.__validator = validator


	def __call__(self, estimand: Estimand) -> Estimation:
		"""
		
		:param estimand: A value to be estimated
		:type estimand: Estimand

		:return: An estimation
		:rtype: Estimation
		"""
		self.__validator(estimand)
		return self.__criterion(estimand)



class Suite(Criterion[Estimation]):
	"""The criterion suite class

	Objects of that class are supposed to iterate through a list of criteria
	until there is a passed one. If so returns the estimation of a passed criterion.
	Otherwise raises AssertionError.
	"""

	def __init__(self, criteria: t.Iterable[Criterion]) -> None:
		"""
		
		:param criteria: A list of criteria to be iterated
		:type criteria: typing.Iterable[Criterion]
		"""
		self.criteria = criteria


	def __call__(self, estimand: Estimand) -> Estimation:
		"""
		
		:param estimand: An estimand
		:type estimand: Estimand

		:return: An estimation
		:rtype: Estimation

		:raises AssertionError: No passed criterion found
		"""
		for crit in self.criteria:
			try:
				return crit(estimand)
			except AssertionError:
				pass
		raise AssertionError
