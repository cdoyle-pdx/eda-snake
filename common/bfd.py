#!/usr/bin/env python3

class Peer:
    def __init__(
            self,
            local_address: str,
            is_session_up: bool,
            down_reason: str,
            intf_name: str,
            jspath: str):
        self.local_address = local_address
        self.is_session_up = is_session_up
        self.down_reason = down_reason
        self.intf_name = intf_name
        self.jspath = jspath
