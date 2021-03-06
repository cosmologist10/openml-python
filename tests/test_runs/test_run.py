from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

from openml.testing import TestBase
from openml.flows.sklearn_converter import sklearn_to_flow
from openml import OpenMLRun


class TestRun(TestBase):
    # Splitting not helpful, these test's don't rely on the server and take less
    # than 1 seconds

    def test_parse_parameters_flow_not_on_server(self):

        model = LogisticRegression()
        flow = sklearn_to_flow(model)
        self.assertRaisesRegexp(ValueError,
                                'Flow sklearn.linear_model.logistic.LogisticRegression '
                                'has no flow_id!',
                                OpenMLRun._parse_parameters, flow)

        model = AdaBoostClassifier(base_estimator=LogisticRegression())
        flow = sklearn_to_flow(model)
        flow.flow_id = 1
        self.assertRaisesRegexp(ValueError,
                                'Flow sklearn.linear_model.logistic.LogisticRegression '
                                'has no flow_id!',
                                OpenMLRun._parse_parameters, flow)

    def test_parse_parameters(self):

        model = RandomizedSearchCV(
            estimator=RandomForestClassifier(n_estimators=5),
            param_distributions={"max_depth": [3, None],
                                 "max_features": [1, 2, 3, 4],
                                 "min_samples_split": [2, 3, 4, 5, 6, 7, 8, 9, 10],
                                 "min_samples_leaf": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                 "bootstrap": [True, False],
                                 "criterion": ["gini", "entropy"]},
            cv=StratifiedKFold(n_splits=2, random_state=1),
            n_iter=5)
        flow = sklearn_to_flow(model)
        flow.flow_id = 1
        flow.components['estimator'].flow_id = 2
        parameters = OpenMLRun._parse_parameters(flow)
        for parameter in parameters:
            self.assertIsNotNone(parameter['oml:component'], msg=parameter)
            if parameter['oml:name'] == 'n_estimators':
                self.assertEqual(parameter['oml:value'], '5')
                self.assertEqual(parameter['oml:component'], 2)
