#!/usr/bin/env python3
"""Unit tests for EDA Metadata module"""

from common import metadata

# INPUT_METADATA_NAME = "test-metadata"
INPUT_METADATA_NS = "test-ns"
INPUT_METADATA_LABELS = {
    "label1": "star",
    "label2": "wars",
    "label3": "star",
    "label4": "trek",
}

INPUT_METADATA_ANNOTATIONS = {
    "anno1": "name=test-metadata",
    "anno2": "fruits.eda.nokia.com/name=oranges",
}
# INPUT_METADATA_DICT = {"name": INPUT_METADATA_NAME, "labels": None}

test_fixtures_objs = [
    {"input": {"name": ""}, "expected": {}},
    {"input": {"name": "", "labels": INPUT_METADATA_LABELS}, "expected": {}},
    {
        "input": {"name": "", "annotations": INPUT_METADATA_ANNOTATIONS},
        "expected": {"annotations": INPUT_METADATA_ANNOTATIONS},
    },
    {
        "input": {"name": "", "namespace": INPUT_METADATA_LABELS},
        "expected": {"namespace": INPUT_METADATA_LABELS},
    },
    {
        "input": {"name": "test-1"},
        "expected": {"name": "test-1", "labels": None},
    },
    {
        "input": {"name": "test-2", "namespace": INPUT_METADATA_NS},
        "expected": {
            "name": "test-2",
            "labels": None,
            "namespace": INPUT_METADATA_NS,
        },
    },
    {
        "input": {
            "name": "test-3",
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
        "expected": {
            "name": "test-3",
            "labels": None,
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
    },
    {
        "input": {
            "name": "test-4",
            "labels": INPUT_METADATA_LABELS,
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
        "expected": {
            "name": "test-4",
            "labels": INPUT_METADATA_LABELS,
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
    },
]

test_fixtures_metadata_objs = [
    {"input": metadata.Metadata.from_name(""), "expected": {}},
    {
        "input": metadata.Metadata.from_name("spanish-inquisition"),
        "expected": {"name": "spanish-inquisition", "labels": None},
    },
    {
        "input": metadata.Metadata("", INPUT_METADATA_NS),
        "expected": {
            "namespace": INPUT_METADATA_NS,
        },
    },
    {
        "input": metadata.Metadata("", INPUT_METADATA_NS, INPUT_METADATA_LABELS),
        "expected": {
            "namespace": INPUT_METADATA_NS,
        },
    },
    {
        "input": metadata.Metadata(
            "", INPUT_METADATA_NS, INPUT_METADATA_LABELS, INPUT_METADATA_ANNOTATIONS
        ),
        "expected": {
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
    },
    {
        "input": metadata.Metadata("testobj1"),
        "expected": {"name": "testobj1", "labels": None},
    },
    {
        "input": metadata.Metadata("testobj2", INPUT_METADATA_NS),
        "expected": {
            "name": "testobj2",
            "labels": None,
            "namespace": INPUT_METADATA_NS,
        },
    },
    {
        "input": metadata.Metadata(
            "testobj3", INPUT_METADATA_NS, annotations=INPUT_METADATA_ANNOTATIONS
        ),
        "expected": {
            "name": "testobj3",
            "labels": None,
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
    },
    {
        "input": metadata.Metadata(
            "testobj4",
            INPUT_METADATA_NS,
            INPUT_METADATA_LABELS,
            INPUT_METADATA_ANNOTATIONS,
        ),
        "expected": {
            "name": "testobj4",
            "labels": INPUT_METADATA_LABELS,
            "namespace": INPUT_METADATA_NS,
            "annotations": INPUT_METADATA_ANNOTATIONS,
        },
    },
]


def test_metadata_sanity():
    """Sanity test for class Metadata"""
    assert metadata.Metadata.from_yaml(None) is None
    assert metadata.Metadata.from_input(None) is None

    for item in test_fixtures_metadata_objs:
        obj = item["input"]
        expected = item["expected"]
        assert isinstance(obj, metadata.Metadata)
        assert obj.to_input() == expected

    for item in test_fixtures_objs:
        input = item["input"]
        expected = item["expected"]
        metadata_metadata = metadata.Metadata(input["name"])
        if input["name"] != "":
            assert metadata_metadata.name == expected["name"]
        # assert metadata_metadata.to_input() == expected

        metadata_fromyaml = metadata.Metadata.from_yaml(input)
        assert isinstance(metadata_fromyaml, metadata.Metadata)
        assert metadata_fromyaml.name == metadata_metadata.name
        assert metadata_fromyaml.to_input() == expected

        metadata_frominput = metadata.Metadata.from_input(input)
        assert isinstance(metadata_frominput, metadata.Metadata)
        assert metadata_frominput.name == metadata_metadata.name
        assert metadata_frominput.to_input() == expected


if __name__ == "__main__":
    test_metadata_sanity()
