#!/usr/bin/env python3
"""Unit tests for EDA IPs"""

from utils import ip


def test_is_ipv4_sanity():
    """Sanity test for function is_ipv4"""
    assert ip.is_ipv4("1.1.1.1") is True
    assert ip.is_ipv4("1.1.1..300") is False


def test_is_ipv6_sanity():
    """Sanity test for function is_ipv6"""
    assert ip.is_ipv6("3ffe::") is True
    assert ip.is_ipv6("cafe::babe:1") is True
    assert ip.is_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
    assert ip.is_ipv6("2001:db8:85a3:0:0:8a2e:370:7334") is True
    assert ip.is_ipv6("2001:db8:85a3::8a2e:370:7334") is True
    assert ip.is_ipv6("2001:db8:85a3::8a2e:370:") is False
    assert ip.is_ipv6("::1") is True
    assert ip.is_ipv6("::") is True
    assert ip.is_ipv6("FE80::0202:B3FF:FE1E:8329") is True
    assert ip.is_ipv6("not.an.ipv6.address") is False
    assert ip.is_ipv6("2001::85a3::8a2e:370:7334") is False
    assert ip.is_ipv6("invalid_ipv6_address") is False
    assert ip.is_ipv6("2000::1.2.3.4") is True
    assert ip.is_ipv6("::1.2.3.4") is True
    assert ip.is_ipv6("2001:0db8:85a3:0000:8a2e:0370:7334:1.2.3.4") is False
    assert ip.is_ipv6("2001:0db8:85a3:8a2e:0370:7334:1.2.3.4") is True
    assert ip.is_ipv6("2001::85a3::8a2e:370:7334:1.2.3.4") is False
    assert ip.is_ipv6("FE80::0202:B3FF:FE1E:8329:1.2.0.0") is True
    assert ip.is_ipv6("FE80::222:0202:B3FF:FE1E:8329:1.2.0.0") is False
    assert ip.is_ipv6("::ffff:1.2.3.4") is True
    assert ip.is_ipv6("1.1.1.0") is False
    assert ip.is_ipv6("1.2.3.4") is False


def test_get_ip_proto_from_address_sanity():
    """Sanity test for function get_ip_proto_from_address"""
    assert ip.get_ip_proto_from_address("1.1.1.1") == "ipv4"
    assert ip.get_ip_proto_from_address("3ffe::") == "ipv6"


def test_prefix_length_to_ipv4_netmask_sanity():
    """Sanity test for function prefix_length_to_ipv4_netmask"""
    assert ip.prefix_length_to_ipv4_netmask(24) == "255.255.255.0"


def test_prefix_length_to_ipv6_netmask_sanity():
    """Sanity test for function prefix_length_to_ipv6_netmask"""
    assert ip.prefix_length_to_ipv6_netmask(64) == "ffff:ffff:ffff:ffff:0000:0000:0000:0000"


def test_compress_ipv6_address():
    """Sanity test for function compress_ipv6_address"""
    assert ip.compress_ipv6_address('caba:dd:00:0:0000:b1') == "caba:dd::b1"
    assert ip.compress_ipv6_address('caba::dd:00:0:b1') == "caba::dd:0:0:b1"
    assert ip.compress_ipv6_address("::") == "::"
    assert ip.compress_ipv6_address("::11:2:4") == "::11:2:4"
    assert ip.compress_ipv6_address("11:3:4::") == "11:3:4::"
    assert ip.compress_ipv6_address("1:cafe::01:1") == "1:cafe::1:1"
    assert ip.compress_ipv6_address("::1:cafe:01") == "::1:cafe:1"
    assert ip.compress_ipv6_address("1:cafe:01:1::") == "1:cafe:1:1::"
    assert ip.compress_ipv6_address("0:cafe:0:00:00:1:2:2") == "0:cafe::1:2:2"
    assert ip.compress_ipv6_address("0:0:11:0:0:0:0:1") == "0:0:11::1"
    assert ip.compress_ipv6_address("0:0:0:11:0:0:0:1") == "::11:0:0:0:1"
    assert ip.compress_ipv6_address("0:0:11:0:0:0:0:0") == "0:0:11::"
    assert ip.compress_ipv6_address("0:0:11:0:0:0:0:1.2.3.4") == "0:0:11::102:304"
    assert ip.compress_ipv6_address("0:0:ffff:1.2.3.4") == "::ffff:102:304"
    assert ip.compress_ipv6_address("2002::2.2.2.2") == "2002::202:202"
    assert ip.compress_ipv6_address("1001::1.1.1.1") == "1001::101:101"


def test_get_addresses_in_subnet():
    """Sanity test for function test_get_addresses_in_subnet"""
    assert len(ip.get_addresses_in_subnet('caba:dd:00::b1/120', 4)) == 4
    assert len(ip.get_addresses_in_subnet('192.168.3.10/24', 4)) == 4
    assert len(ip.get_addresses_in_subnet('192.168.3.10/24', 2)) == 2
    assert len(ip.get_addresses_in_subnet('caba:dd:00::b1/120', 2)) == 2


def test_netmask_to_prefix_length():
    """Sanity test for function test_netmask_to_prefix_length"""
    assert ip.netmask_to_prefix_length('255.255.0.0') == 16
    assert ip.netmask_to_prefix_length('255.255.240.0') == 20
    assert ip.netmask_to_prefix_length('255.255.255.0') == 24
    assert ip.netmask_to_prefix_length('255.255.255.240') == 28


def test_getipprefix_withoutmask():
    """Sanity test for function test_getipprefix_withoutmask"""
    assert ip.getipprefix_withoutmask('172.22.22.24/24') == "172.22.22.24"
    assert ip.getipprefix_withoutmask('178.22.22.24') == "178.22.22.24"


def test_get_network_for_address():
    """Sanity test for function test_get_network_for_address"""
    assert ip.get_network_for_address('172.22.22.24/24') == "172.22.22.0/24"
    assert ip.get_network_for_address('178.22.22.24/16') == "178.22.0.0/16"
    assert ip.get_network_for_address("cafe:babe::120/120") == "cafe:babe::100/120"
    assert ip.get_network_for_address("cafe:babe:abcd:3343:556::11/96") == "cafe:babe:abcd:3343:556::/96"
    assert ip.get_network_for_address("cafe:babe:abcd:3343:556::11/64") == "cafe:babe:abcd:3343::/64"


if __name__ == "__main__":
    test_is_ipv4_sanity()
    test_is_ipv6_sanity()
    test_get_ip_proto_from_address_sanity()
    test_prefix_length_to_ipv4_netmask_sanity()
    test_prefix_length_to_ipv6_netmask_sanity()
    test_compress_ipv6_address()
    test_get_addresses_in_subnet()
    test_netmask_to_prefix_length()
    test_getipprefix_withoutmask()
    test_get_network_for_address()
