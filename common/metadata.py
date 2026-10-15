#!/usr/bin/env python3

Y_METADATA = 'metadata'
Y_NAME = 'name'
Y_LABELS = 'labels'
Y_ANNOTATIONS = 'annotations'
Y_NAMESPACE = 'namespace'


class Metadata:
    def __init__(self,
                 name: str,
                 namespace: str = None,
                 labels: dict = None,
                 annotations: dict = None):
        self.name = name
        self.namespace = namespace
        self.labels = labels
        self.annotations = annotations

    def to_input(self):
        _rval = {}
        if self.name:
            _rval[Y_NAME] = self.name
        if self.name:
            _rval[Y_LABELS] = self.labels
        if self.namespace:
            _rval[Y_NAMESPACE] = self.namespace
        if self.annotations:
            _rval[Y_ANNOTATIONS] = self.annotations
        return _rval

    @staticmethod
    def from_yaml(obj):
        if obj:
            _name = obj.get(Y_NAME, None)
            _namespace = obj.get(Y_NAMESPACE, None)
            _labels = obj.get(Y_LABELS, None)
            _annotations = obj.get(Y_ANNOTATIONS, None)
            return Metadata(
                name=_name,
                namespace=_namespace,
                labels=_labels,
                annotations=_annotations)
        return None

    @staticmethod
    def from_input(obj):
        if obj:
            _name = obj.get(Y_NAME, None)
            _namespace = obj.get(Y_NAMESPACE, None)
            _labels = obj.get(Y_LABELS, None)
            _annotations = obj.get(Y_ANNOTATIONS, None)
            return Metadata(
                name=_name,
                namespace=_namespace,
                labels=_labels,
                annotations=_annotations)
        return None

    @staticmethod
    def from_name(_name: str):
        return Metadata(name=_name,)
