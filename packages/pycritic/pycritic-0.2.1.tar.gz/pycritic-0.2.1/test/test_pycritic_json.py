import pytest

import pycritic.json



@pytest.fixture
def suiteBuilder():
	return pycritic.json.DefaultSuiteBuilder()



RAW_SAMPLE_SUITE = {
	"crit": [
		{
			"est": {
				"mark": 2,
				"comment": "Eww... Josh?.." # Just kidding; name does not matter :)
			},
			"cond": {
				"courier_name": { "regex": "^Josh.*$" }
			}
		},
		{
			"est": {
				"mark": 5,
				"comment": "High quality goods and fast delivery. Just flawless"
			},
			"cond": {
				"delivery_time": { "le": 30 },
				"quality": 5,
				"package": 5,
				"courier_politeness": { "ge": 4 }
			}
		},
		{
			"est": {
				"mark": 4,
				"comment": "Good quality and delivery. Well done!"
			},
			"cond": {
				"delivery_time": { "ge": 0, "le": 45 },
				"quality": { "ge": 4 },
				"package": { "ge": 3 },
				"courier_politeness": { "ge": 4 }
			}
		},
		{
			"est": {
				"mark": 4,
				"comment": "Rude courier"
			},
			"cond": {
				"delivery_time": { "le": 30 },
				"quality": 5,
				"package": { "ge": 4 },
				"courier_politeness": { "le": 3 }
			}
		},
		{
			"est": {
				"mark": 3,
				"comment": "Discount carries"
			},
			"cond": {
				"discount_ratio": { "ge": .15 }
			}
		},
		{
			"est": {
				"mark": 1,
				"comment": "I'm disappointed!"
			}
		}
	],

	"schema": {
		"$schema": "http://json-schema.org/draft-04/schema#",
		"type": "object",
		"properties": {
			"delivery_time": { "type": "number" },
			"quality": { "$ref": "#/definitions/mark5" },
			"package": { "$ref": "#/definitions/mark5" },
			"courier_politeness": { "$ref": "#/definitions/mark5" },
			"courier_name": { "type": "string" },
			"discount_ratio": {
				"type": "number",
				"minimum": 0,
				"maximum": 1
			}
		},
		"required": [
			"delivery_time",
			"quality",
			"package",
			"courier_politeness",
			"discount_ratio"
		],
		"definitions": {
			"mark5": {
				"type": "integer",
				"minimum": 1,
				"maximum": 5
			}
		}
	}
}



@pytest.fixture
def sampleSuite(suiteBuilder):
	return suiteBuilder(RAW_SAMPLE_SUITE)

	

@pytest.mark.parametrize("delivery,expected", (
	(
		{
			"delivery_time": 25,
			"quality": 4,
			"package": 5,
			"courier_politeness": 5,
			"courier_name": "John Doe",
			"discount_ratio": 0
		},
		4
	),
	(
		{
			"delivery_time": 90,
			"quality": 3,
			"package": 3,
			"courier_politeness": 4,
			"courier_name": "Jane Foe",
			"discount_ratio": .05
		},
		1
	),
	(
		{
			"delivery_time": 90,
			"quality": 3,
			"package": 3,
			"courier_politeness": 4,
			"courier_name": "James Boe",
			"discount_ratio": .15
		},
		3
	),
	(
		{
			"delivery_time": 29,
			"quality": 5,
			"package": 5,
			"courier_politeness": 5,
			"courier_name": "John Doe",
			"discount_ratio": .10
		},
		5
	),
	(
		{
			"delivery_time": 25,
			"quality": 5,
			"package": 5,
			"courier_politeness": 5,
			"courier_name": "Josh Moe",
			"discount_ratio": .12
		},
		2
	)
))
def testCritic(delivery, expected, sampleSuite):
	est = sampleSuite(delivery)
	assert expected == est["mark"]
