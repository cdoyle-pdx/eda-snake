#!/usr/bin/env python3
"""Unit tests for EDA IPs"""

from utils import version


def test_version_sanity():
    """Sanity test for function compare_version"""
    assert version.compare("23.10.r1", "23.10.r2") == -1
    assert version.compare("23.10.r11", "23.11.1") == -1
    assert version.compare("23.10.r1", "23.9.r2") == 1
    assert version.compare("23.10.r1", "23.10.r1") == 0
    assert version.compare("23.10.r1", "23.10.R1") == 0
    assert version.compare("23.10.r1", "22.10.r1") == 1
    assert version.compare("23.10", "22.10.r1") == 1


if __name__ == "__main__":
    test_version_sanity()
