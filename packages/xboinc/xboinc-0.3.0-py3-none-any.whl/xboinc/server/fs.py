# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2024.                 #
# ######################################### #

import os, subprocess
from pathlib import Path
from time import sleep
import random

from .tools import log_debug, log_info, log_error


# Functions to work with the AFS file system
# ==========================================

def on_afs(file):
    parents = list(fs_path(file).parents)
    if len(parents) < 3:
        return False
    else:
        return parents[-3] == Path('/afs/cern.ch')

def afs_add_acl(user, directory, acl='rlwik', cmd=None, is_server=False):
    cmd = 'afs_add_acl' if cmd is None else cmd
    try:
        directory = fs_path(directory)
        cmd = subprocess.run(['fs', 'sa', directory, user, acl],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            log_info(f"Set ACL '{acl}' on directory {directory} for user {user}.", cmd=cmd, is_server=is_server)
            return 0
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Failed to set ACL '{acl}' on {directory} for user {user}.\n{stderr}", cmd=cmd, is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed to set ACL '{acl}' on {directory} for user {user}.\n{stderr}", e, cmd=cmd, is_server=is_server)
        return 1


def afs_remove_acl(user, directory, cmd=None, is_server=False):
    cmd = 'afs_remove_acl' if cmd is None else cmd
    try:
        directory = fs_path(directory)
        cmd = subprocess.run(['fs', 'sa', directory, user, 'none'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            log_info(f"Removed ACL on directory {directory} for user {user}.", cmd=cmd, is_server=is_server)
            return 0
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Failed to remove ACL on {directory} for user {user}.\n{stderr}", cmd=cmd, is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed to remove ACL on {directory} for user {user}.\n{stderr}", e, cmd=cmd, is_server=is_server)
        return 1


def afs_print_acl(directory, cmd=None, is_server=False):
    cmd = 'afs_print_acl' if cmd is None else cmd
    try:
        directory = fs_path(directory)
        cmd = subprocess.run(['fs', 'la', directory],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            stdout = cmd.stdout.decode('UTF-8').strip().split('\n')
            log_info(f"{stdout}", cmd=cmd, is_server=is_server)
            return 0
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Failed to print ACL on {directory} for user {user}.\n{stderr}", cmd=cmd, is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed to print ACL on {directory} for user {user}.\n{stderr}", e, cmd=cmd, is_server=is_server)
        return 1


# Functions to work with the EOS file system
# ==========================================

EOS_MGM_URL = 'root://eosuser.cern.ch'
eos_env = {**os.environ, 'EOS_MGM_URL': EOS_MGM_URL}

def on_eos(file):
    parents = list(fs_path(file).parents)
    if len(parents) < 2:
        return False
    else:
        return parents[-2] == Path('/eos')

def eos_installed():
    try:
        cmd = subprocess.run(['eos', '--version'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=eos_env)
        # Temporary hack as the eos command wrongly returns 255
        return cmd.returncode == 0 or cmd.returncode == 255
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def missing_eos(message='', cmd=None, is_server=False):
    cmd = 'missing_eos' if cmd is None else cmd
    if eos_installed():
        return 0
    else:
        message = '' if message == '' else f"{message} "
        log_error(f"{message}EOS is not installed on your system.",
                  EnvironmentError(), cmd=cmd, is_server=is_server)
        return 1


def eos_command_for_find():
    # The command `eos find` has the wrong behaviour on new machines (running eos 5.2).
    # For this reason, the command `eos oldfind` has been introduced.
    # However, this command does not exist on the old machines, so in that case we
    # default back to `eos find`.
    cmd = subprocess.run(['eos', 'oldfind'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=eos_env)
    if cmd.returncode == 255:
        # Command not found; we are running on a machine running old eos < 5.2
        return 'find'
    else:
        # Command found; we are running on a machine running new eos >= 5.2
        return 'oldfind'

# def xrdcp_installed():
#     try:
#         cmd = subprocess.run(["xrdcp", "--version"], stdout=subprocess.PIPE,
#                              stderr=subprocess.PIPE, check=True)
#         return cmd.returncode == 0
#     except (subprocess.CalledProcessError, FileNotFoundError):
#         return False


# General file IO functions
# =========================

def _dir(directory):
    directory = Path(directory)
    if not directory.is_dir() or f'{directory}'[-1] == '/':
        return f'{directory}'
    else:
        return f'{directory}/'

def fs_path(path):
    path = Path(path).expanduser().resolve()
    return Path(path.as_posix().replace('/eos/home-','/eos/user/'))

def fs_glob(path, pattern, cmd=None, is_server=False):
    cmd = 'fs_glob' if cmd is None else cmd
    path = fs_path(path)
    err_mess = f"Failed fs_glob {pattern} in {path}!"
    try:
        if on_eos(path):
            if missing_eos(err_mess):
                return []
            cmd = subprocess.run(['eos', eos_command_for_find(), '-name', pattern, f'{path}'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=eos_env)
        else:
            cmd = subprocess.run(['find', f'{path}', '-name', pattern],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmd.returncode != 0 or cmd.stdout == b'':
            return []
        files = [fs_path(ss) for ss in cmd.stdout.decode('UTF-8').split()]
        return [f for f in files if fs_exists(f)]
    except Exception as e:
        log_error(f"{err_mess}\n", e, cmd=cmd, is_server=is_server)
        return []

def fs_exists(file, cmd=None, is_server=False):
    cmd = 'fs_exists' if cmd is None else cmd
    file = fs_path(file)
    err_mess = f"Failed fs_exists for {file}!"
    try:
        if on_eos(file):
            if missing_eos(err_mess):
                return False
            cmd = subprocess.run(['eos', eos_command_for_find(), '-name', file.name,
                                  f'{file.parent}'], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, env=eos_env)
            if cmd.returncode != 0 or cmd.stdout == b'':
                # Command failed, assume file not found
                return False
            files = cmd.stdout.decode('UTF-8').split()
            if len(files) == 0:
                # File not found
                return False
            # If the file is found, we need to ensure that it is not empty
            # This command will list zero-length files
            cmd = subprocess.run(['eos', eos_command_for_find(), '-0', '-name', file.name,
                                  f'{file.parent}'], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, env=eos_env)
            if cmd.returncode != 0 or cmd.stdout == b'':
                # Command failed, assume no empty file found
                return True
            return len(cmd.stdout.decode('UTF-8').split()) == 0
        else:
            return file.exists() and file.stat().st_size!=0
    except Exception as e:
        log_error(f"{err_mess}\n", e, cmd=cmd, is_server=is_server)
        return False

def fs_rm(file, cmd=None, is_server=False):
    cmd = 'fs_rm' if cmd is None else cmd
    file = fs_path(file)
    err_mess = f"Failed fs_rm for {file}!"
    try:
        if on_eos(file):
            if missing_eos(err_mess):
                return 1
            cmd = subprocess.run(['eos', 'rm', '-r', _dir(file)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env=eos_env)
        else:
            cmd = subprocess.run(['rm', '-r', f'{file}'], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            return 0
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"{err_mess}\n{stderr}", cmd=cmd, is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"{err_mess}\n", e, cmd=cmd, is_server=is_server)
        return 1


# Always use the following functions file by file, not for a list of files

def fs_cp(file, directory, maximum_trials=10, wait=2.7, cmd=None, is_server=False):
    cmd = 'fs_cp' if cmd is None else cmd
    file   = fs_path(file)
    directory = fs_path(directory)
    if file.parent == directory:
        return 0
    if not directory.is_dir():
        log_error(f"Failed fs_cp: {directory} is not a directory!", cmd=cmd, is_server=is_server)
        return 1
    err_mess = f"Failed fs_cp {file} to {directory}!"
    try:
        for i in range(maximum_trials):
            if on_eos(file) or on_eos(directory):
                if missing_eos(err_mess):
                    return 1
                cmd = subprocess.run(['eos', 'cp', f'{file}', _dir(directory)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env=eos_env)
            else:
                cmd = subprocess.run(['cp', f'{file}', f'{directory}'],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd.returncode == 0 and fs_exists(directory / file.name):
                return 0
            if i != maximum_trials-1:
                log_debug(f"{err_mess}\nRetrying ({i})..", cmd=cmd, is_server=is_server)
                sleep(abs(wait+random.normalvariate(0, 0.1*wait)))
        log_error(f"{err_mess}\n", cmd=cmd, is_server=is_server)
        if not fs_exists(directory / file.name):
            log_error(f"Command succeeds but destination file is not created!\n",
                      cmd=cmd, is_server=is_server)
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Command failed: {stderr}\n", cmd=cmd, is_server=is_server)
        log_error("Giving up.", cmd=cmd, is_server=is_server)
        return 1
    except Exception as e:
        log_error(f"{err_mess}\n", e, cmd=cmd, is_server=is_server)
        return 1

def fs_rename(file, new_file, maximum_trials=10, wait=2.7, cmd=None, is_server=False):
    cmd = 'fs_rename' if cmd is None else cmd
    file     = fs_path(file)
    new_file = fs_path(new_file)
    if file.parent != new_file.parent:
        log_error(f"Failed fs_rename: {file} not in the same directory as {new_file}!",
                  cmd=cmd, is_server=is_server)
        return 1
    err_mess = f"Failed fs_rename {file} to {new_file}!"
    try:
        for i in range(maximum_trials):
            if on_eos(file):
                if missing_eos(err_mess):
                    return 1
                cmd = subprocess.run(['eos', 'mv', f'{file}', new_file],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env=eos_env)
            else:
                cmd = subprocess.run(['mv', f'{file}', new_file],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd.returncode == 0 and fs_exists(new_file):
                return 0
            if i != maximum_trials-1:
                log_debug(f"{err_mess}\nRetrying ({i})..", cmd=cmd, is_server=is_server)
                sleep(abs(wait+random.normalvariate(0, 0.1*wait)))
        log_error(f"{err_mess}\n", cmd=cmd, is_server=is_server)
        if not fs_exists(new_file):
            log_error(f"Command succeeds but destination file is not created!\n",
                      cmd=cmd, is_server=is_server)
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Command failed: {stderr}\n", cmd=cmd, is_server=is_server)
        log_error("Giving up.", cmd=cmd, is_server=is_server)
        return 1
    except Exception as e:
        log_error(f"{err_mess}\n", e, cmd=cmd, is_server=is_server)
        return 1

def fs_mv(file, directory, maximum_trials=10, wait=2.7, cmd=None, is_server=False):
    cmd = 'fs_mv' if cmd is None else cmd
    new_file = None
    if not directory.is_dir():
        new_file = directory
        directory = directory.parent
    cp_failed = fs_cp(file, directory, maximum_trials, wait, cmd=cmd, is_server=is_server)
    # returncode 0 means success
    if cp_failed: return 1
    if new_file is not None:
        # rename
        mv_failed = fs_rename(directory / file.name, new_file,
                              maximum_trials, wait, cmd=cmd, is_server=is_server)
        if mv_failed: return 1
    if fs_exists(file, cmd=cmd, is_server=is_server):
        return fs_rm(file, cmd=cmd, is_server=is_server)
    return 0


