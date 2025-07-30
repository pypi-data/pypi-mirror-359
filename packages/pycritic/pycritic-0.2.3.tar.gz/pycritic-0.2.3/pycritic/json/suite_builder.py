import typing as t

import logging
import pprint

import json
import jsonschema

from ..base import Estimation, Criterion, ValidatingCriterion, Suite

from .criterion_builder import \
	CriterionBuilder, DefaultCriterionBuilder



class DefaultSuiteBuilder(CriterionBuilder[Estimation]):
	"""Default suite builder
	
	The suite builder which is used by default
	"""

	CRITERION_BUILDER = DefaultCriterionBuilder()
	"""Criterion builder"""

	CRITERIA_KEY = "crit"
	"""Key of the criteria parameter in a config"""

	ESTIMAND_SCHEMA_KEY = "schema"
	"""Key of the schema parameter in a config"""

	SCHEMA_ENV_KEY = "PYCRITIC_SUITE_SCHEMA"
	"""Key of the environmental variable storing path to a schema for a suite"""

	DEFAULT_SCHEMA = {
		"$schema": "http://json-schema.org/draft-04/schema#",
		"title": "PyCritic default suite",
		"type": "object",
		"properties": {
			"schema": {
				"title": "Schema of an estimand",
				"type": "object",
				"additionalProperties": True
			},
			"crit": {
				"title": "A criteria list",
				"type": "array",
				"items": {
					"title": "A criterion",
					"type": "object",
					"properties": {
						"est": {
							"title": "An estimation"
						},
						"cond": {
							"title": "A condition list",
							"type": "object",
							"additionalProperties": True
						}
					},
					"required": [
						"est"
					]
				},
				"minItems": 0
			}
		}
	}
	"""Default schema for a suite"""


	def __init__(self, schemaFilename: t.Union[str, None] = None) -> None:
		if schemaFilename:
			self.__loadSuiteSchema(schemaFilename)
		else:
			self.__setDefaultSuiteSchema()


	def __loadSuiteSchema(self, schemaFilename: str) -> None:
		logging.warning(f"Loading suite schema from '{schemaFilename}'")
		with open(schemaFilename) as file:
			self.__schema = json.load(file)


	def __setDefaultSuiteSchema(self) -> None:
		logging.warning("No suite schema filename given; using the default suite schema")
		logging.debug(pprint.pformat(DefaultSuiteBuilder.DEFAULT_SCHEMA))
		self.__schema = DefaultSuiteBuilder.DEFAULT_SCHEMA


	def __call__(self, raw: t.Any) -> Criterion[Estimation]:
		"""
		
		Validates the parameter value using the schema and decides which one criterion to create

		:param raw: A raw data to convert
		:type raw: typing.Any

		:return: A criterion
		:rtype: Criterion[Estimation]
		"""
		jsonschema.validate(raw, self.__schema)

		if not isinstance(raw, t.Mapping):
			raise TypeError("mapping expected")
		
		rawCriteria = raw[DefaultSuiteBuilder.CRITERIA_KEY]
		criteria = list(map(DefaultSuiteBuilder.CRITERION_BUILDER, rawCriteria))

		baseSuite = Suite(criteria)

		try:
			schema = raw[DefaultSuiteBuilder.ESTIMAND_SCHEMA_KEY]
			validator = lambda raw: jsonschema.validate(raw, schema)
			return ValidatingCriterion(baseSuite, validator)
		except KeyError:
			return baseSuite
