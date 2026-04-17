"""Tests for sky.provision.kubernetes.instance helpers."""

from sky.provision.kubernetes import instance

CLUSTER = 'my-cluster'


def _spread_term():
    return {
        'weight': 100,
        'podAffinityTerm': {
            'labelSelector': {
                'matchExpressions': [{
                    'key': instance.TAG_SKYPILOT_CLUSTER_NAME,
                    'operator': 'In',
                    'values': [CLUSTER],
                }],
            },
            'topologyKey': 'kubernetes.io/hostname',
        },
    }


def test_merge_spread_anti_affinity_empty_spec():
    pod_spec = {'spec': {}}
    instance._merge_spread_anti_affinity(pod_spec, CLUSTER)
    assert pod_spec['spec']['affinity'] == {
        'podAntiAffinity': {
            'preferredDuringSchedulingIgnoredDuringExecution': [_spread_term()],
        },
    }


def test_merge_spread_anti_affinity_preserves_user_node_affinity():
    user_node_affinity = {
        'requiredDuringSchedulingIgnoredDuringExecution': {
            'nodeSelectorTerms': [{
                'matchExpressions': [{
                    'key': 'kubernetes.io/hostname',
                    'operator': 'In',
                    'values': ['10.140.80.58', '10.140.81.74'],
                }],
            }],
        },
    }
    pod_spec = {'spec': {'affinity': {'nodeAffinity': user_node_affinity}}}

    instance._merge_spread_anti_affinity(pod_spec, CLUSTER)

    affinity = pod_spec['spec']['affinity']
    assert affinity['nodeAffinity'] == user_node_affinity
    assert affinity['podAntiAffinity'][
        'preferredDuringSchedulingIgnoredDuringExecution'] == [_spread_term()]


def test_merge_spread_anti_affinity_appends_to_existing_anti_affinity():
    user_term = {
        'weight': 50,
        'podAffinityTerm': {
            'labelSelector': {
                'matchLabels': {
                    'app': 'other'
                },
            },
            'topologyKey': 'topology.kubernetes.io/zone',
        },
    }
    pod_spec = {
        'spec': {
            'affinity': {
                'podAntiAffinity': {
                    'preferredDuringSchedulingIgnoredDuringExecution': [
                        user_term
                    ],
                },
            },
        },
    }

    instance._merge_spread_anti_affinity(pod_spec, CLUSTER)

    preferred = pod_spec['spec']['affinity']['podAntiAffinity'][
        'preferredDuringSchedulingIgnoredDuringExecution']
    assert preferred == [user_term, _spread_term()]
