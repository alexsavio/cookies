#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Install the packages you have listed in the requirements file you input as
first argument.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fabric.api import task, local, cd
from fabric.context_managers import warn_only

import sys
import os
import os.path as op
import fileinput
import subprocess
import shutil
from fnmatch import fnmatch
from glob import glob
from setuptools import Command, setup, find_packages
from pip.req import parse_requirements

#get current dir
CWD = op.realpath(op.curdir)

#LIST OF PATTERNS OF FILENAMES to IGNORE
IGNORE_PATS = {'.git'}

#File that holds a list of the projects
PROJECTS_LIST = 'neurita_projects'


def get_working_projects(projslist_filepath=PROJECTS_LIST):
    try:
        return open(projslist_filepath).read().split()
    except:
        raise IOError('Could not find file {}'.format(projslist_filepath))


def is_ignored(value, ignore_list=IGNORE_PATS):
    for ign in ignore_list:
        if fnmatch(value, ign):
            return True

    return False


def recursive_glob(base_directory, regex=None):
    """
    Uses glob to find all files or folders that match the regex
    starting from the base_directory.

    Parameters
    ----------
    base_directory: str

    regex: str

    Returns
    -------
    files: list

    """
    if regex is None:
        regex = ''

    base_path = op.realpath(base_directory)
    matches = glob(os.path.join(base_path, regex))
    for root, dirs, files in os.walk(base_path, topdown=True):
        dirs[:] = [d for d in dirs if not is_ignored(d)]
        for dir in dirs:
            try:
                matches.extend(glob(op.join(op.realpath(root), dir, regex)))
            except:
                print('Error globbing {}'.format(op.join(op.realpath(root), dir, regex)))
                raise

    return matches


def recursive_remove(work_dir=CWD, regex='*'):
    for fn in recursive_glob(work_dir, regex):
        os.remove(fn)
        print("removed '{}'".format(fn))


def recursive_rmtrees(work_dir=CWD, regex='*'):
    for dn in recursive_glob(work_dir, regex):
        shutil.rmtree(dn, ignore_errors=True)
        print("removed '{}'".format(dn))


@task
def install_deps():
    #for line in fileinput.input():
    req_filepaths = ['carbon/config/neurita-requirements.txt']

    deps = get_requirements(*req_filepaths)

    try:
        for dep_name in deps:
            cmd = "pip install '{0}'".format(dep_name)
            print('#', cmd)
            subprocess.check_call(cmd, shell=True)
    except:
        print('Error installing {}'.format(dep_name))


@task
def clean(work_dir=CWD):
    clean_build(work_dir)
    clean_pyc(work_dir)


@task
def clean_build(work_dir=CWD):
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    recursive_rmtrees(work_dir, '__pycache__')
    recursive_rmtrees(work_dir, '*.egg-info')


@task
def clean_pyc(work_dir=CWD):
    recursive_remove(work_dir, '*.pyc')
    recursive_remove(work_dir, '*.pyo')
    recursive_remove(work_dir, '*~')


@task
def lint(module_name='carbon'):
    local('flake8 ' + module_name + ' test')


@task
def test():
    local('py.test')


@task
def test_all():
    local('tox')


@task
def docs(module_name, doc_type='html'):
    os.remove(op.join('docs', module_name + '.rst'))
    os.remove(op.join('docs', 'modules.rst'))
    local('sphinx-apidoc -o docs/ ' + module_name)
    os.chdir('docs')
    local('make clean')
    local('make ' + doc_type)
    os.chdir(CWD)
    local('open docs/_build/html/index.html')


@task
def release(module_name):
    os.chdir(module_name)
    local('fab release')
    os.chdir(CWD)


@task
def release(module_name):
    os.chdir(module_name)
    local('fab sdist')
    os.chdir(CWD)


@task
def push(module_name, remote='origin', branch='master'):
    os.chdir(module_name)
    print('Pushing ' + op.realpath(op.curdir))
    local('git push {} {}'.format(remote, branch))
    os.chdir(CWD)


@task
def pull(module_name, remote='origin', branch='master'):
    os.chdir(module_name)
    print('Pulling ' + op.realpath(op.curdir))
    local('git pull {} {}'.format(remote, branch))
    os.chdir(CWD)


@task
def commit(module_name, msg):
    os.chdir(module_name)
    print('Commit {} '.format(op.realpath(op.curdir)))
    local('git commit -a -m "{}"'.format(msg))
    os.chdir(CWD)


@task
def gitadd(module_name, filename):
    os.chdir(module_name)
    print('Adding {} to {}'.format(filename, op.realpath(op.curdir)))
    local('git add "{}"'.format(filename))
    os.chdir(CWD)


@task
def pull_all(remote='origin', branch='master'):
    proj_names = get_working_projects()
    for proj in proj_names:
        pull(proj, remote, branch)
        print('\n')


@task
def push_all(remote='origin', branch='master'):
    proj_names = get_working_projects()
    for proj in proj_names:
        push(proj, remote, branch)
        print('\n')


@task
def commit_all(msg):
    proj_names = get_working_projects()
    for proj in proj_names:
        commit(proj, msg)
        print('\n')


@task
def gitadd_all(filename):
    proj_names = get_working_projects()
    print(proj_names)
    for proj in proj_names:
        gitadd(proj, filename)
        print('\n')
