# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2024.                 #
# ######################################### #

import json
import os
from pathlib import Path

from .general import _pkg_root
from .user import update_user_data, get_user_data, remove_user
from .server import server_account, dropdir, fs_exists, fs_rm, fs_cp,\
                    afs_add_acl, afs_remove_acl, on_afs, on_eos, fs_path, fs_rename


user_data_file = _pkg_root / 'user_data.json'


def _create_json(user, directory, remove=False):
    register = 'deregister' if remove else 'register'
    user_file = Path.cwd() / f'{register}_{user}.json'
    if remove:
        data = {'user': user}
    else:
        directory = fs_path(directory)
        if on_eos(directory):
            domain = 'eos'
        elif on_afs(directory):
            domain = 'afs'
        else:
            raise ValueError(f"Directory {directory} not on EOS nor AFS! "
                            + "The xboinc server will not be able to reach it.")
        data = {'user': user, 'directory': f'{directory}', 'domain': domain}
    with user_file.open('w') as f:
        json.dump(data, f)
    return user_file, data


def _give_rights(directory, domain, acl='rlwikd'):
    if domain == 'eos':
        raise NotImplementedError("Ask CERN IT for explanation...")
    else:
        afs_add_acl(server_account, directory, acl=acl)


def _remove_rights(directory, domain):
    if domain == 'eos':
        raise NotImplementedError("Ask CERN IT for explanation...")
    else:
        afs_remove_acl(server_account, directory)


def register(user, directory):
    """
    Register a user to the BOINC server and dev server, by declaring
    the username and user boinc directory, and giving access rights
    to the BOINC admin process. This is not instantaneous, as the
    BOINC server periodically parses new users.

    Parameters
    ----------
    user : string
        Name of the user to register.
    directory : pathlib.Path
        Dedicated folder that the BOINC server can reach (i.e. on CERN
        AFS or EOS), which will hold the new submissions and results.
        Should not be accessed manually by the user to avoid syncing
        issues.

    Returns
    -------
    None.
    """

    assert_eos_accessible()
    directory = fs_path(directory)
    if not directory.is_dir():
        raise ValueError(f"Directory {directory} not found or not a directory (or no permissions)!")
    user_file, data = _create_json(user, directory)
    # This is a small hack to avoid losing sixtadm ACLs during testing
    acl = 'rlwikda' if user==server_account else 'rlwikd'
    try:
        _give_rights(directory, data['domain'], acl=acl)
    except Exception as e:
        user_file.unlink()
        raise e
    input_dir      = directory / 'input'
    input_dev_dir  = directory / 'input_dev'
    output_dir     = directory / 'output'
    output_dev_dir = directory / 'output_dev'
    input_dir.mkdir(parents=True, exist_ok=True)
    input_dev_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dev_dir.mkdir(parents=True, exist_ok=True)
    try:
        _give_rights(input_dir, data['domain'], acl=acl)
        _give_rights(input_dev_dir, data['domain'], acl=acl)
        _give_rights(output_dir, data['domain'], acl=acl)
        _give_rights(output_dev_dir, data['domain'], acl=acl)
    except Exception as e:
        user_file.unlink()
        raise e
    if fs_exists(dropdir / f'de{user_file.name}'):
        fs_rm(dropdir / f'de{user_file.name}')
        print("Removed existing deregistration file on server dropdir.")
    if fs_exists(dropdir / f'dev_de{user_file.name}'):
        fs_rm(dropdir / f'dev_de{user_file.name}')
    if fs_exists(dropdir / user_file.name):
        fs_rm(dropdir / user_file.name)
        print("Replaced existing registration file on server dropdir.")
    if fs_exists(dropdir / f'dev_{user_file.name}'):
        fs_rm(dropdir / f'dev_{user_file.name}')
    try:
        fs_cp(user_file, dropdir, maximum_trials=1)
        fs_rename(dropdir / user_file.name, dropdir / f'dev_{user_file.name}', maximum_trials=1)
        fs_cp(user_file, dropdir, maximum_trials=1)
    except:
        user_file.unlink()
        raise Exception(f"Failed to copy register file to server dropdir.\n"
                       + "Do you have permissions?\n"
                       + "If not, add yourself to the CERN xboinc-submitters egroup.")
    user_file.unlink()
    update_user_data(user, data)


def deregister(user):
    """
    Remove a user from the BOINC server and dev server.  This is
    not instantaneous, as the BOINC server periodically parses
    the users to remove.

    Parameters
    ----------
    user : string
        Name of the user to deregister.

    Returns
    -------
    None.
    """

    assert_eos_accessible()
    user_file, _ = _create_json(user, '', remove=True)
    try:
        data = get_user_data(user)
    except ValueError:
        print(f"User {user} not found in user_data.")
    else:
        directory = fs_path(data['directory'])
        # This is a quick check to avoid losing sixtadm ACLs during testing
        if user!=server_account:
            try:
                input_dir      = directory / 'input'
                input_dev_dir  = directory / 'input_dev'
                output_dir     = directory / 'output'
                output_dev_dir = directory / 'output_dev'
                _remove_rights(input_dir, data['domain'])
                _remove_rights(input_dev_dir, data['domain'])
                _remove_rights(output_dir, data['domain'])
                _remove_rights(output_dev_dir, data['domain'])
                _remove_rights(directory, data['domain'])
            except:
                print(f"Warning: could not remove ACL on {data['directory']} for server "
                    + f"account {server_account}!\nPlease do this manually.")
    if fs_exists(dropdir / user_file.name[2:]):
        fs_rm(dropdir / user_file.name[2:])
        print("Removed existing registration file on server dropdir.")
    if fs_exists(dropdir / f'dev_{user_file.name[2:]}'):
        fs_rm(dropdir / f'dev_{user_file.name[2:]}')
    try:
        fs_cp(user_file, dropdir, maximum_trials=1)
        fs_rename(dropdir / user_file.name, dropdir / f'dev_{user_file.name}', maximum_trials=1)
        fs_cp(user_file, dropdir, maximum_trials=1)
    except:
        user_file.unlink()
        raise Exception(f"Failed to copy deregister file to server dropdir.\n"
                      + f"Please inform an xboinc admin to deregister manually.")
    user_file.unlink()
    remove_user(user)
