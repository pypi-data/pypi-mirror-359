from abc import ABC, abstractmethod
import typing as t

from ..base import Estimation, Criterion, BasicCriterion

from .checker_builder import DefaultCheckerBuilder



class CriterionBuilder(ABC, t.Generic[Estimation]):
	"""Criterion builder base class
	
	Converts given raw data into a criterion.
	"""

	@abstractmethod
	def __call__(self, raw: t.Any) -> Criterion[Estimation]:
		"""
		
		:param raw: Raw data to be converted
		:type raw: typing.Any

		:return: Criterion[Estimation]
		"""
		pass



class ValidatingCriterionBuilder(CriterionBuilder[Estimation]):
	"""Validating criterion builder; decorator
	
	Validates provided raw data before creating a criterion.
	"""

	def __init__(
		self,
		criterionBuilder: CriterionBuilder[Estimation],
		validator: t.Callable[[t.Any], None]
	) -> None:
		"""

		:param criterionBuilder: A basic criterion builder
		:type criterionBuilder: CriterionBuilder[Estimation]

		:param validator: Raw data validating function
		:type validator: typing.Callable[[t.Any], None]
		"""
		self.__criterionBuilder = criterionBuilder
		self.__validator = validator


	def __call__(self, raw: t.Any) -> Criterion[Estimation]:
		"""
		
		:param raw: Raw data to be converted
		:type raw: typing.Any

		:return: A criterion
		:rtype: Criterion[Estimation]
		"""
		self.__validator(raw)
		return self.__criterionBuilder(raw)



class DefaultCriterionBuilder(CriterionBuilder[Estimation]):
	"""Default criterion builder
	
	The criterion builder which is used by default.
	"""

	CHECKER_BUILDER = lambda paramName, rawConditions: \
		DefaultCheckerBuilder(paramName)(rawConditions)
	"""The checker-building function"""

	ESTIMATION_KEY = "est"
	"""Key of the estimation parameter in a config"""

	CHECKERS_KEY = "cond"
	"""Key of the condition list in a config"""


	def __call__(self, raw: t.Any) -> Criterion[Estimation]:
		"""
		
		:param raw: Raw data to be converted
		:type raw: typing.Any

		:return: A criterion
		:rtype: Criterion[Estimation]
		"""
		if not isinstance(raw, t.Mapping):
			raise TypeError("mapping expected", raw)

		rawCheckers = raw.get(DefaultCriterionBuilder.CHECKERS_KEY, {})
		checkers = [
			DefaultCriterionBuilder.CHECKER_BUILDER(paramName, rawConditions)
			for paramName, rawConditions in rawCheckers.items()
		]

		estimation = raw[DefaultCriterionBuilder.ESTIMATION_KEY]
		return BasicCriterion(estimation, checkers)
