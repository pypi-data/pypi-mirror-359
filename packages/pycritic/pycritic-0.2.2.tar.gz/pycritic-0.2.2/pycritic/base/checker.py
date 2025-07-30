from abc import ABC, abstractmethod
import typing as t



Estimand = t.Mapping[str, t.Any]
"""The estimand generic type"""

Condition = t.Callable[[t.Any], bool]
"""Callable object suppose to return a boolean value on a given argument"""



class Checker(ABC):
	"""Checker base class

	Objects of that class are supposed to return a boolean value as a reaction
	on a given estimand.
	"""

	@abstractmethod
	def __call__(self, estimand: Estimand) -> bool:
		"""
		
		:param estimand: An estimand
		:type estimand: Estimand

		:return: A boolean value
		:rtype: bool
		"""
		pass



class SingleConditionChecker(Checker):
	"""Singly-conditioned checker
	
	Checks a single estimand parameter with a single condition.
	"""

	def __init__(self, paramName: str, condition: Condition) -> None:
		"""
		
		:param paramName: Name of the parameter to be extracted from an estimand and estimated then
		:type paramName: str

		:param condition: A condition to be checked
		:type condition: Condition
		"""
		self.__paramName = paramName
		self.__condition = condition
	

	def __call__(self, estimand: Estimand) -> bool:
		"""

		:param estimand: An estimand
		:type estimand: Estimand

		:return: Either True or False
		:rtype: bool
		"""
		value = estimand[self.__paramName]
		return self.__condition(value)



class MultiConditionChecker(Checker):
	"""Multiply-conditioned checker
	
	Checks a single parameter with a list of conditions.
	"""

	def __init__(
		self,
		paramName: str,
		conditions: t.Iterable[Condition]
	) -> None:
		"""

		:param paramName: Name of the parameter to be extracted from an estimand and estimated then
		:type paramName: str

		:param conditions: A list of conditions to be applied to the parameter
		:type conditions: typing.Iterable[Condition]
		"""
		self.__paramName = paramName
		self.__conditions = conditions


	def __call__(self, estimand: Estimand) -> bool:
		"""
	
		:param estimand: An estimand
		:type estimand: Estimand

		:return: Either True or False
		:rtype: bool
		"""
		value = estimand[self.__paramName]
		return all(cond(value) for cond in self.__conditions)
