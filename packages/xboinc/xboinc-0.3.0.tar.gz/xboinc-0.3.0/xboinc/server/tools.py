# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2024.                 #
# ######################################### #

from pathlib import Path
import logging as lg
import traceback
import tarfile
import datetime



def timestamp(ms=False, in_filename=True):
    ms = -3 if ms else -7
    if in_filename:
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:ms]
    else:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:ms]


def log_debug(message, cmd=None, is_server=False):
    if is_server:
        cmd = '' if cmd is None else f'  {cmd}:'
        lg.debug(f"DEBUG {timestamp(ms=True, in_filename=False)}"
               + f"{cmd}  {message}")
    else:
        print(message)

def log_info(message, cmd=None, is_server=False):
    if is_server:
        cmd = '' if cmd is None else f'  {cmd}:'
        lg.info(f"INFO  {timestamp(ms=True, in_filename=False)}"
               + f"{cmd}  {message}")
    else:
        print(message)

def log_error(message, e=None, cmd=None, is_server=False):
    if is_server:
        cmd = '' if cmd is None else f'  {cmd}:'
        lg.error(f"ERROR {timestamp(ms=True, in_filename=False)}"
               + f"{cmd}  {message}", exc_info=True)
    else:
        raise Exception(message, e)


def untar(filename, cmd=None, is_server=False):
    cmd = 'untar' if cmd is None else cmd
    try:
        filename = Path(filename)
        thisdir = filename.parent / filename.stem[:-4]
        thisdir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(filename, 'r:gz') as fid:
            fid.extractall(path=thisdir)
        filename.unlink()
        log_debug(f"Extracted {filename}.", cmd=cmd, is_server=is_server)
    except Exception as e:
        log_error(f"Failed extracting {filename}", e, cmd=cmd, is_server=is_server)

