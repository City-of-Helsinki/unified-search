# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_importer_end_results 1'] = {
    'hits': [
        {
            '_id': 'baz',
            '_index': 'test_1',
            '_score': 1.0,
            '_source': {
                'foo': 'import number 1'
            }
        }
    ],
    'max_score': 1.0,
    'total': {
        'relation': 'eq',
        'value': 1
    }
}

snapshots['test_importer_end_results 2'] = {
    'test_1': {
        'aliases': {
            'test': {
            }
        }
    }
}

snapshots['test_importer_end_results 3'] = {
    'hits': [
        {
            '_id': 'baz',
            '_index': 'test_2',
            '_score': 1.0,
            '_source': {
                'foo': 'import number 2'
            }
        }
    ],
    'max_score': 1.0,
    'total': {
        'relation': 'eq',
        'value': 1
    }
}

snapshots['test_importer_end_results 4'] = {
    'test_2': {
        'aliases': {
            'test': {
            }
        }
    }
}

snapshots['test_importer_end_results 5'] = {
    'hits': [
        {
            '_id': 'baz',
            '_index': 'test_1',
            '_score': 1.0,
            '_source': {
                'foo': 'import number 3'
            }
        }
    ],
    'max_score': 1.0,
    'total': {
        'relation': 'eq',
        'value': 1
    }
}

snapshots['test_importer_end_results 6'] = {
    'test_1': {
        'aliases': {
            'test': {
            }
        }
    }
}

snapshots['test_importer_wip_results[does not have old data] 1'] = {
    'hits': [
        {
            '_id': 'foo',
            '_index': 'test_1',
            '_score': 1.0,
            '_source': {
                'foo': 'new data'
            }
        }
    ],
    'max_score': 1.0,
    'total': {
        'relation': 'eq',
        'value': 1
    }
}

snapshots['test_importer_wip_results[does not have old data] 2'] = {
    'test_1': {
        'aliases': {
            'test': {
            },
            'test_wip': {
            }
        }
    }
}

snapshots['test_importer_wip_results[has old data] 1'] = {
    'hits': [
        {
            '_id': 'foo',
            '_index': 'test_1',
            '_score': 1.0,
            '_source': {
                'foo': 'old data'
            }
        }
    ],
    'max_score': 1.0,
    'total': {
        'relation': 'eq',
        'value': 1
    }
}

snapshots['test_importer_wip_results[has old data] 2'] = {
    'test_1': {
        'aliases': {
            'test': {
            }
        }
    },
    'test_2': {
        'aliases': {
            'test_wip': {
            }
        }
    }
}
