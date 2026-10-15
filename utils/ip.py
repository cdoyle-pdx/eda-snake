#!/usr/bin/env python3

import re
import utils.exceptions as e


def is_ipv4(ip_addr):
    return True if re.match(r"^\d+\.\d+\.\d+\.\d+", ip_addr) else False


def is_ipv6(ip_addr):
    # print("ip_addr: ", ip_addr)
    if ip_addr.endswith(":") and not ip_addr.endswith("::"):
        return False

    single_col_parts = ip_addr.split(":")
    double_col_parts = ip_addr.split("::")

    if len(single_col_parts) == 1:
        return False

    # check for uncompressed address, single_col_parts should not be more than 8
    # for compressed address, double_col_parts should not be more 2
    if len(single_col_parts) > 8 or len(double_col_parts) > 2:
        return False
    parts = []
    if len(double_col_parts) == 1:
        parts = single_col_parts
    elif len(double_col_parts) == 2:
        parts = double_col_parts[0].split(":") + double_col_parts[1].split(":")
    else:
        return False

    if "." in parts[-1] and len(double_col_parts) == 1 and len(parts) > 7:
        return False
    elif "." in parts[-1] and len(double_col_parts) == 2 and len(parts) >= 7:
        return False
    elif len(parts) > 8:
        return False

    if '.' in parts[-1]:
        # ipv4 part of ipv6 address needs 4 bytes (2 Hextets)
        # check if its valid ipv4 address
        if is_ipv4(parts[-1]) is False:
            return False
        parts = parts[:-1]  # validate only hextet below

    for part in parts:
        if not part:
            continue  # Empty parts are valid because they represent compressed sections
        # Check if each part is a valid hexadecimal number
        if len(part) > 4:  # pragma: no cover
            return False
        try:
            # Try converting the part to an integer with base 16
            int(part, 16)
        except ValueError:  # pragma: no cover
            # If conversion fails, it's not a valid hexadecimal number
            return False

    # If all checks passed, the address is valid
    return True


def get_ip_proto_from_address(ip_addr):
    return 'ipv4' if re.match(r"^\d+\.\d+\.\d+\.\d+", ip_addr) else 'ipv6'


def getipprefix_withoutmask(ip_prefix: str):
    ip_prefix_woslash = None
    index_of_slash = -1
    if ip_prefix is not None:
        index_of_slash = ip_prefix.find("/")
    if index_of_slash != -1:
        ip_prefix_woslash = ip_prefix[:index_of_slash]
    else:
        ip_prefix_woslash = ip_prefix
    return ip_prefix_woslash


def netmask_to_prefix_length(netmask):
    """
    Converts a netmask address to an integer.
    """
    mask_parts = netmask.split(".")
    mask_num = 0
    for part in mask_parts:
        mask_num += bin(int(part)).count("1")
    return mask_num


def prefix_length_to_ipv4_netmask(prefix_length):
    # Ensure that the prefix length is valid
    if not (0 <= prefix_length <= 32):  # pragma: no cover
        raise e.InvalidInput("Invalid IPv4 prefix length")
    # Calculate the subnet mask using bitwise operations
    subnet_mask = (1 << 32) - (1 << (32 - prefix_length))
    # Convert the subnet mask to dotted-decimal format
    subnet_mask_str = ".".join([str((subnet_mask >> i) & 0xFF) for i in (24, 16, 8, 0)])
    return subnet_mask_str


def prefix_length_to_ipv6_netmask(prefix_length):
    # Ensure that the prefix length is valid
    if not (0 <= prefix_length <= 128):  # pragma: no cover
        raise e.InvalidInput("Invalid IPv6 prefix length")
    # Calculate the network address
    network_address = "1" * prefix_length + "0" * (128 - prefix_length)
    # Split the network address into 8 groups of 16 bits
    groups = [network_address[i:i + 16] for i in range(0, 128, 16)]
    # Convert each group to hexadecimal and join them with colons
    # subnet_mask_str = ":".join([hex(int(group, 2))[2:].zfill(4) for group in groups])
    subnet_mask_str = ":".join(['{:0>{w}}'.format(hex(int(group, 2))[2:], w=4) for group in groups])
    return subnet_mask_str


def compress_ipv6_address(ipv6_address):
    hextets = _get_hextets_from_ipv6_str(ipv6_str=ipv6_address)
    best_doublecolon_start = -1
    best_doublecolon_len = 0
    doublecolon_start = -1
    doublecolon_len = 0
    for index, hextet in enumerate(hextets):
        if re.match(r'^0*$', hextet) is None:
            hextets[index] = hextet.lstrip("0")
            doublecolon_len = 0
            doublecolon_start = -1
        else:
            hextets[index] = '0'
            doublecolon_len += 1
            if doublecolon_start == -1:
                # Start of a sequence of zeros.
                doublecolon_start = index
            if doublecolon_len > best_doublecolon_len:
                # This is the longest sequence of zeros so far.
                best_doublecolon_len = doublecolon_len
                best_doublecolon_start = doublecolon_start

    if best_doublecolon_len > 1:
        best_doublecolon_end = (best_doublecolon_start +
                                best_doublecolon_len)
        # For zeros at the end of the address.
        if best_doublecolon_end == len(hextets):
            hextets += ['']
        hextets[best_doublecolon_start:best_doublecolon_end] = ['']
        # For zeros at the beginning of the address.
        if best_doublecolon_start == 0:
            hextets = [''] + hextets

    compr_str = ':'.join(hextets)
    return compr_str.lower()


def _get_hextets_from_ipv6_str(ipv6_str):
    v6_addr = _expand_ipv4_mapped_ipv6(ipv6_str=ipv6_str)
    segments = v6_addr.split(":")

    if '' in segments:
        if v6_addr == "::":
            segments = ['0'] * 8
        elif v6_addr.startswith("::"):
            segments = ['0'] * (9 - len(segments) + 1) + segments[2:]
        elif v6_addr.endswith("::"):
            segments = segments[:-2] + ['0'] * (9 - len(segments) + 1)
        else:
            double_colon_index = segments.index('')
            num_missing_groups = 9 - len(segments)  # Total groups in an IPv6 address is 8
            expanded_groups = ['0'] * num_missing_groups
            segments[double_colon_index:double_colon_index + 1] = expanded_groups
    return segments


def _expand_ipv4_mapped_ipv6(ipv6_str):
    # If ends with an IPv4 address (contains '.')
    if '.' in ipv6_str:
        ipv6_part, ipv4_part = ipv6_str.rsplit(':', 1)
        if is_ipv4(ipv4_part) is False:
            raise ValueError(f"Invalid IPv4-mapped IPv6 address: {ipv6_str}")
        octets = ipv4_part.split('.')
        # Convert to 2 hextets
        high = (int(octets[0]) << 8) + int(octets[1])
        low = (int(octets[2]) << 8) + int(octets[3])
        ipv6_str = f"{ipv6_part}:{high:04x}:{low:04x}"
    return ipv6_str


def convert_ipv6_to_int(ipv6_str):
    """Converts an IPv6 address string to a 128-bit integer."""
    segments = _get_hextets_from_ipv6_str(ipv6_str=ipv6_str)
    ip_int = 0
    for i, hextet in enumerate(segments[::-1]):
        ip_int += int(hextet, 16) << (16 * i)
    return ip_int


def convert_int_to_ipv6(ip_int):
    """Converts a 128-bit integer to an IPv6 address string."""

    hextets = []
    for i in range(8):
        hextet = (ip_int >> (16 * i)) & 0xFFFF
        hextets.append(f"{hextet:04x}")
    return ":".join(hextets[::-1])


def get_addresses_in_subnet(subnet_cidr, limit):
    """Return first requested number of addresses in given subnet_cidr"""

    # Parse CIDR notation
    network, prefix_length = subnet_cidr.split('/')
    prefix_length = int(prefix_length)
    if ':' in network:
        if not (0 <= prefix_length <= 128):  # pragma: no cover
            raise e.InvalidInput("Invalid IPv6 prefix length")
        ip_int = convert_ipv6_to_int(network)
        netmask = (2**128 - 1) << (128 - prefix_length)
        network_address = ip_int & netmask
        addresses = []
        num_hosts = 2**(128 - prefix_length)
        if num_hosts == 2:
            # include network and broadcast address:
            addresses = [compress_ipv6_address(convert_int_to_ipv6(network_address)) + f'/{prefix_length}', compress_ipv6_address(convert_int_to_ipv6(network_address + 1)) + f'/{prefix_length}']
            return addresses
        if num_hosts <= limit:  # pragma: no cover
            limit = num_hosts - 2
        for i in range(network_address + 1, network_address + limit + 1):
            addresses.append(compress_ipv6_address(convert_int_to_ipv6(i)) + f'/{prefix_length}')
        return addresses

    else:
        if not (0 <= prefix_length <= 32):  # pragma: no cover
            raise e.InvalidInput("Invalid IPv4 prefix length")
        mask_val = (1 << 32) - (1 << (32 - prefix_length))
        mask_octets = [int((mask_val >> i) & 0xFF) for i in (24, 16, 8, 0)]
        network_octets = [int(octet) for octet in network.split('.')]
        # Calculate network address
        network_address = [ip & mask for ip, mask in zip(network_octets, mask_octets)]
        # Calculate number of hosts in the subnet
        addresses = []
        num_hosts = 2 ** (32 - sum(bin(mask).count('1') for mask in mask_octets))
        if num_hosts == 2:
            # include network and broadcast address:
            addresses = [network_address, tuple(network_address[j] + (1 >> (24 - 8 * j)) & 0xFF for j in range(4))]
            return ['.'.join(map(str, address)) + f'/{prefix_length}' for address in addresses]

        if num_hosts <= limit:  # pragma: no cover
            limit = num_hosts - 2
        for i in range(1, limit + 1):
            next_address = tuple(network_address[j] + (i >> (24 - 8 * j)) & 0xFF for j in range(4))
            addresses.append(next_address)
        return ['.'.join(map(str, address)) + f'/{prefix_length}' for address in addresses]


def get_first_ipv6_unicast_address_in_subnet(subnet_cidr):
    """Return first unicast address in given ipv6 subnet_cidr"""

    # Parse CIDR notation
    network, prefix_length = subnet_cidr.split('/')
    prefix_length = int(prefix_length)
    if not (0 < prefix_length < 128):  # pragma: no cover
        raise e.InvalidInput("Invalid IPv6 prefix length")
    ip_int = convert_ipv6_to_int(network)
    netmask = (2**128 - 1) << (128 - prefix_length)
    network_address = ip_int & netmask
    if prefix_length == 127:
        return f"{compress_ipv6_address(convert_int_to_ipv6(network_address))}/{prefix_length}"
    else:
        return f"{compress_ipv6_address(convert_int_to_ipv6(network_address + 1))}/{prefix_length}"


def get_network_for_address(cidr_addr):
    # Parse CIDR notation
    network, prefix_length = cidr_addr.split('/')
    prefix_length = int(prefix_length)
    if ':' in network:
        # ipv6 cidr
        if not (0 <= prefix_length <= 128):  # pragma: no cover
            raise e.InvalidInput("Invalid IPv6 prefix length")
        ip_int = convert_ipv6_to_int(network)
        netmask = (2**128 - 1) << (128 - prefix_length)
        nw_addr_int = ip_int & netmask
        nw_addr_str = compress_ipv6_address(convert_int_to_ipv6(nw_addr_int))
        return f'{nw_addr_str}/{prefix_length}'
    else:
        # ipv4 cidr
        if not (0 <= prefix_length <= 32):  # pragma: no cover
            raise e.InvalidInput("Invalid IPv4 prefix length")
        mask_val = (1 << 32) - (1 << (32 - prefix_length))
        mask_octets = [int((mask_val >> i) & 0xFF) for i in (24, 16, 8, 0)]
        network_octets = [int(octet) for octet in network.split('.')]
        # Calculate network address
        nw_addr_int = [ip & mask for ip, mask in zip(network_octets, mask_octets)]
        nw_addr_str = tuple(nw_addr_int[j] & 0xFF for j in range(4))
        return '.'.join(map(str, nw_addr_str)) + f'/{prefix_length}'


def get_compressed_prefix_mask(subnet: str):
    comp_prefix_mask = subnet
    parts = subnet.split('/')
    if len(parts) == 2:
        prefix_part = parts[0]
        mask = parts[1]
        if is_ipv6(prefix_part) and mask is not None:
            prefix = compress_ipv6_address(prefix_part)
            comp_prefix_mask = f'{prefix}/{mask}'
    return comp_prefix_mask


if __name__ == "__main__":  # pragma: no cover
    print(get_addresses_in_subnet('cafe:baba:cd::1/125', 20))
    print(get_addresses_in_subnet('10.20.10.1/30', 5))
    print(get_addresses_in_subnet('fc00::c0a8:0/127', 2))
    print(get_addresses_in_subnet('fc00::c0a8:0:0/127', 2))
    print(netmask_to_prefix_length('255.255.0.0'))
    print(prefix_length_to_ipv4_netmask(28))
    print(prefix_length_to_ipv6_netmask(120))
    print(getipprefix_withoutmask('172.22.22.24/24'))
    print(getipprefix_withoutmask('182.22.22.24'))
    print(get_compressed_prefix_mask('2026:802::0/64'))
    print(get_compressed_prefix_mask('22.22.1.1/24'))
    print(get_compressed_prefix_mask('2026:802::0'))
    print(get_compressed_prefix_mask('54.22.1.1'))

    print("::", "->", compress_ipv6_address("::"))
    print("::11:2:4", "-> ", compress_ipv6_address("::11:2:4"))
    print("11:3:4::", "-> ", compress_ipv6_address("11:3:4::"))
    print("1:cafe::01:1", "-> ", compress_ipv6_address("1:cafe::01:1"))
    print("::1:cafe:01", "-> ", compress_ipv6_address("::1:cafe:01"))
    print("1:cafe:01:1::", "-> ", compress_ipv6_address("1:cafe:01:1::"))
    print("1:cafe:00:1::", "-> ", compress_ipv6_address("1:cafe:00:1::"))
    print("0:cafe:0:00:00:1:2:2", "-> ", compress_ipv6_address("0:cafe:0:00:00:1:2:2"))
    print("1:cafe:00:1::", "-> ", compress_ipv6_address("1:cafe:00:1::"))
    print("0:0:11:0:0:0:0:1", "-> ", compress_ipv6_address("0:0:11:0:0:0:0:1"))
    print("2001:DB8:AAA:397::2", "-> ", compress_ipv6_address("2001:DB8:AAA:397::2"))
    print("0:0:11:22:1.2.0.0", "-> ", compress_ipv6_address("0:0:11:22:1.2.0.0"))
    print("2001:0db8:85a3:8a2e:0370:7334:55.21.3.4", "-> ", compress_ipv6_address("2001:0db8:85a3:8a2e:0370:7334:55.21.3.4"))

    print("10.20.30.11/16", "-> ", get_network_for_address("10.20.30.11/16"))
    print("10.20.30.11/30", "-> ", get_network_for_address("10.20.30.11/30"))
    print("cafe:babe::120/120", "-> ", get_network_for_address("cafe:babe::120/120"))
    print("cafe:babe:abcd:3343:556::11/64", "-> ", get_network_for_address("cafe:babe:abcd:3343:556::11/64"))
