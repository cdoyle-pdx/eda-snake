class JPathParser:
    def __init__(self, jpath):
        self.jpath = jpath
        self.parse_jpath()

    def parse_jpath(self):
        self.nodes = []
        self.nodes_with_keys = {}
        self.keys = []
        self.values = []
        node = ''
        key = ''
        value = ''
        reading = 'node'  # can be 'node', 'key', or 'value'
        for c in self.jpath:
            if reading == 'node':
                if c == '.':
                    if node:
                        self.nodes.append(node)
                        if node not in self.nodes_with_keys:
                            self.nodes_with_keys[node] = {}
                    node = ''
                elif c == '{':
                    reading = 'key'
                else:
                    node += c
            elif reading == 'key':
                if c == '=':
                    if key:
                        self.keys.append(key)
                    reading = 'value'
                elif c != '.':
                    key += c
            elif reading == 'value':
                if c == '"':
                    continue
                elif c == '}':
                    reading = 'node'
                    self.values.append(value)
                    if node:
                        self.nodes_with_keys[node] = {"key": key, "value": value}
                    key = ''
                    value = ''
                elif c != '=':
                    value += c
        if node and node not in self.nodes:
            self.nodes.append(node)
            if node not in self.nodes_with_keys:
                self.nodes_with_keys[node] = {}

    def get_nodes(self):
        return self.nodes

    def get_nodes_with_keys(self):
        return self.nodes_with_keys

    def get_keys(self):
        return self.keys[::-1]  # Reverse the list to get most recent key first

    def get_values(self):
        return self.values[::-1]  # Reverse the list to get most recent value first

    def get_nodes_with_values(self):
        return {node: self.nodes_with_keys[node].get('value', '') for node in self.nodes}

    def get_last_node(self):
        return self.nodes[-1] if self.nodes else ''

    def get_last_key(self):
        return self.nodes_with_keys[self.get_last_node()].get('key', '') if self.get_last_node() in self.nodes_with_keys else ''

    def get_last_value(self):
        return self.nodes_with_keys[self.get_last_node()].get('value', '') if self.get_last_node() in self.nodes_with_keys else ''
