import pytest
import pycritic.base



SUITE = pycritic.base.Suite([
	pycritic.base.BasicCriterion(0, [
		pycritic.base.SingleConditionChecker(
			"status",
			lambda status: status == "fired"
		)
	]),
	pycritic.base.BasicCriterion(5, [
		pycritic.base.SingleConditionChecker(
			"reputation",
			lambda reputation: reputation >= .9
		)
	]),
	pycritic.base.BasicCriterion(5, [
		pycritic.base.SingleConditionChecker(
			"effectiveness",
			lambda effectiveness: effectiveness >= .95
		)
	]),
	pycritic.base.BasicCriterion(4, [
		pycritic.base.SingleConditionChecker(
			"effectiveness",
			lambda effectiveness: effectiveness >= .8
		)
	]),
	pycritic.base.BasicCriterion(2, [
		pycritic.base.SingleConditionChecker(
			"experience",
			lambda experience: experience >= 2
		),
		pycritic.base.SingleConditionChecker(
			"effectiveness",
			lambda effectiveness: effectiveness >= .5
		)
	]),
	pycritic.base.BasicCriterion(1)
])



EMPLOYEES = [
	{
		"name": "John Doe",
		"status": "hired",
		"reputation": .95,
		"effectiveness": .75,
		"experience": 15
	},
	{
		"name": "Jane Foe",
		"status": "hired",
		"reputation": .8,
		"effectiveness": .96,
		"experience": 1
	},
	{
		"name": "James Boe",
		"status": "fired",
		"reputation": .2,
		"effectiveness": .43,
		"experience": 2
	},
	{
		"name": "Stanley Moe",
		"status": "hired",
		"reputation": .7,
		"effectiveness": .75,
		"experience": 3
	},
	{
		"name": "Michael Daueaux",
		"status": "hired",
		"reputation": .5,
		"effectiveness": .5,
		"experience": 0
	},
]



@pytest.mark.parametrize("employeeId,expectedEst", (
	(0, 5),
	(1, 5),
	(2, 0),
	(3, 2),
	(4, 1)
))
def testSuite(employeeId, expectedEst):
	assert expectedEst == SUITE(EMPLOYEES[employeeId])
