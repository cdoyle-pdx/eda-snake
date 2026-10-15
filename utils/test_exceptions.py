#!/usr/bin/env python3
"""Unit tests for EDA exceptions"""

from utils import exceptions as e


def test_version_error_sanity():
    """Sanity test for class VersionError"""
    version_error = e.VersionError("interfaces.eda.nokia.com/v1alpha1", "interfaces.eda.nokia.com/v1")
    assert version_error.msg == "version from cr (interfaces.eda.nokia.com/v1alpha1) does not match intent version (interfaces.eda.nokia.com/v1)"


def test_version_missing_dependency_sanity():
    """Sanity test for class MissingDependency"""
    missing_dependency = e.MissingDependency("Interface", "dut1-ethernet-1/3")
    assert missing_dependency.msg == "missing dependency of type Interface with name dut1-ethernet-1/3"


def test_version_invalid_telemetry_sanity():
    """Sanity test for class InvalidTelemetry"""
    invalid_telemetry = e.InvalidTelemetry('.interface{.name=="ethernet-1/3"}', '"unable to infer interface ethernet-1/3')
    assert invalid_telemetry.msg == 'invalid telemetry at path .interface{.name=="ethernet-1/3"}: "unable to infer interface ethernet-1/3'


if __name__ == "__main__":
    test_version_error_sanity()
    test_version_missing_dependency_sanity()
    test_version_invalid_telemetry_sanity()
