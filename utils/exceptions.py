#!/usr/bin/env python3

import eda_config


def VersionError(version_cr: str, version):
    return eda_config.ConfigError(
        msg=f'version from cr ({version_cr}) does not match intent version ({version})',
        values={'version_cr': version_cr, 'version': version})


def MissingDependency(type, name: str):
    return eda_config.ConfigError(
        msg=f'missing dependency of type {type} with name {name}',
        values={'type': type, 'name': name}
    )


def InvalidTelemetry(path: str, message: str):
    return eda_config.ConfigError(
        msg=f'invalid telemetry at path {path}: {message}',
        values={'path': path, 'message': message}
    )


def InvalidInput(msg: str):
    return eda_config.ConfigError(msg=msg)


def MissingParameter(msg: str):
    return eda_config.ConfigError(msg=msg)
