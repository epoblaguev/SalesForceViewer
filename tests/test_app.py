from collections import OrderedDict

from hypothesis import given, strategies as strats

from models import salesforce_connector

STATIC_RESULT = OrderedDict([
    ('totalSize', 2),
    ('done', True),
    ('records', [
        # Record 1
        OrderedDict([
            ('attributes', OrderedDict([
                ('type', 'Sample_Transaction_vod__c'),
                ('url', '/services/data/v29.0/sobjects/Sample_Transaction_vod__c/a0e36000002GNETEST')
            ])),
            ('Id', 'a0e36000002GNETEST'),
            ('Account_vod__r', OrderedDict([
                # Sub Record
                ('attributes', OrderedDict([
                    ('type', 'Account'),
                    ('url', '/services/data/v29.0/sobjects/Account/0013600000Io3JTEST')
                ])),
                ('FirstName', 'Firstey'),
                ('LastName', 'McLastname')

            ])),
            ('CreatedDate', '2016-06-01T18:12:29.000+0000')
        ]),
        # Record 2
        OrderedDict([
            ('attributes', OrderedDict([
                ('type', 'Sample_Transaction_vod__c'),
                ('url', '/services/data/v29.0/sobjects/Sample_Transaction_vod__c/a0e36000002GsbTEST')
            ])),
            ('Id', 'a0e36000002GsbTEST'),
            ('Account_vod__r', None),
            ('CreatedDate', '2016-06-06T23:59:04.000+0000')
        ])
    ])
])

HYPOTHESIS_RESULT = OrderedDict([
    ('totalSize', strats.integers(1)),
    ('done', strats.booleans()),
    ('records', strats.lists(min_size=1, elements=
    strats.fixed_dictionaries(
        OrderedDict([
            ('attributes', strats.fixed_dictionaries(OrderedDict([
                ('type', strats.text()),
                ('url', strats.text())
            ]))),
            ('Id', strats.text()),
            ('Account_vod__r', strats.fixed_dictionaries(OrderedDict([
                # Sub Record
                ('attributes', strats.fixed_dictionaries(OrderedDict([
                    ('type', strats.text()),
                    ('url', strats.text())
                ]))),
                ('FirstName', strats.text()),
                ('LastName', strats.text())

            ]))),
            ('CreatedDate', strats.text())
        ]))
                             ))
])


def test_clean_results():
    raw_results = STATIC_RESULT
    expected = salesforce_connector.Results(
        totalSize=2,
        size=2,
        done=True,
        headers=['Id', 'Account_vod__r', 'CreatedDate'],
        records=[
            ['a0e36000002GNETEST', '[FirstName: Firstey] [LastName: McLastname]', '2016-06-01T18:12:29.000+0000'],
            ['a0e36000002GsbTEST', None, '2016-06-06T23:59:04.000+0000']
        ],
        raw_records=raw_results['records']
    )

    assert expected == salesforce_connector._clean_results(raw_results)


def test_flatten_record():
    raw_record_1 = STATIC_RESULT['records'][0]
    raw_record_2 = STATIC_RESULT['records'][1]

    exp_record_1 = ['a0e36000002GNETEST', '[FirstName: Firstey] [LastName: McLastname]', '2016-06-01T18:12:29.000+0000']
    exp_record_2 = ['a0e36000002GsbTEST', None, '2016-06-06T23:59:04.000+0000']

    assert exp_record_1 == [salesforce_connector._flatten_record_value(val) for val in raw_record_1.values()]
    assert exp_record_2 == [salesforce_connector._flatten_record_value(val) for val in raw_record_2.values()]


@given(strats.fixed_dictionaries(HYPOTHESIS_RESULT))
def test_clean_results_hypothesis(mapping):
    salesforce_connector._clean_results(mapping)
