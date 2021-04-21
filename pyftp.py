#!/usr/bin/env python2

''' A simple Python 2 implementation of an FTP client that uses some functions of the ftplib module. Written by Danilo Santos '''

import argparse
import ftplib
import sys
import re

def _cd(path):
    try:
        FTP.cwd(path)
        print('')
    except ftplib.error_perm, e:
        em = re.sub(r'^[0-9]* ', '', str(e))
        print('cd: cannot access \'%s\': %s\n' % (path, em))

def _ls():
    FTP.retrlines('LIST')
    print('')

def _get(remote_filename, local_filename):
    files = FTP.nlst()

    if remote_filename not in files:
        print('get: cannot download \'%s\': No such file or directory,\n' % remote_filename)
        return

    try:
        FTP.retrbinary('RETR '+remote_filename, open(local_filename, 'wb').write)
        print('\'%s\' successfully downloaded.\n' % local_filename)
    except Exception, e:
        em = re.sub(r'^[0-9]* ', '', str(e))
        print('get: cannot download \'%s\': %s\n' % (remote_filename, em))

def _put(local_filename, remote_filename):
    try:
        _fp = open(local_filename, 'rb')
        FTP.storbinary('STOR '+remote_filename, _fp)
        _fp.close()
        print('\'%s\' successfully uploaded.\n' % remote_filename)
    except ftplib.error_perm, e:
        em = re.sub(r'[0-9]* ".*" ', '', str(e))
        print('put: cannot upload \'%s\': %s\n' % (local_filename, em))
    except IOError:
        print('put: cannot upload \'%s\': No such file or directory\n' % local_filename)
    except ftplib.error_temp, e:
        em = re.sub(r'[0-9]* ".*" ', '', str(e))
        print('put: cannot upload \'%s\': %s\n' % (local_filename, em))

def _rm(filename):
    try:
        FTP.delete(filename)
        print('\'%s\' successfully deleted.\n' % filename)
    except ftplib.error_perm, e:
        em = re.sub(r'[0-9]* ".*" ', '', str(e))
        print('rm: error removing \'%s\': %s\n' % (filename, em))
    except ftplib.error_temp, e:
        em = re.sub(r'[0-9]* ".*" ', '', str(e))
        print('rm: error removing \'%s\': %s\n' % (filename, em))

def _mkdir(directory_name):
    try:
        FTP.mkd(directory_name)
        print('\'%s\' successfully created.\n' % directory_name)
    except ftplib.error_perm, e:
        em = re.sub(r'^[0-9]* ', '', str(e))
        print('mkdir: error creating \'%s\': %s\n' % (directory_name, em))

def _rmdir(directory_name):
    try:
        FTP.rmd(directory_name)
        print('\'%s\' successfully deleted.\n' % directory_name)
    except ftplib.error_perm, e:
        em = re.sub(r'[0-9]* ".*" ', '', str(e))
        print('rmdir: error removing \'%s\': %s\n' % (directory_name, em))

def _show_help(command):
    if command == '':
        print('Available commands:\n\ncd     ls     get\nput    pwd    help\nrm     quit   mkdir\nrmdir\n')
        print('Type help <command> to show detailed help for <command>')
    elif command == 'cd':
        print('cd <path> - change the current directory to <path>')
    elif command in ['dir', 'l', 'll', 'ls']:
        print('ls - list directory contents')
        print('Aliases: dir, l, ll')
    elif command == 'get':
        print('get <remote_filename> [local_filename] - download <remote_filename> to local machine')
        print('If an third argument is supplied, save the file as [local_filename]')
    elif command == 'put':
        print('put <local_filename> [remote_filename] - upload <local_filename> to remote machine')
        print('If an third argument is supplied, save the file as [remote_filename]')
    elif command == 'pwd':
        print('pwd - print name of current/working directory')
    elif command in ['help', '?']:
        print('help [command] - display available commands')
        print('If an second argument is supplied, display instructions on how to use [command]')
        print('Alias: ?')
    elif command in ['del', 'rm']:
        print('rm <filename> - remove <filename>')
        print('Aliases: del')
    elif command in ['bye', 'exit', 'quit']:
        print('quit - terminate and return to previous shell and logout')
        print('Aliases: bye, exit')
    elif command in ['mkdir', 'md']:
        print('mkdir <directory_name> - create <directory_name> directory')
        print('Aliases: md')
    elif command in ['rmdir', 'rd']:
        print('rmdir <directory_name> - remove <directory_name> directory')
        print('Aliases: rd')
    else:
        print('help: %s: Command not found' % command)

    print('')

def _pwd():
    print(FTP.pwd())
    print('')

no_pwd = False

parser = argparse.ArgumentParser(description='A Python 2 implementation of an FTP client that uses\
                                 some functions of the ftplib module. Written by Danilo Santos')
parser.add_argument('host', help='Hostname or IP address of the FTP server', type=str)
parser.add_argument('user', help='Username to authenticate to the FTP server', type=str)
parser.add_argument('password', help='Password to authenticate to the FTP server', type=str)
parser.add_argument('--port', help='Port to connect to the FTP server (default 21)', type=int)

a = parser.parse_args()

if a.port is None:
    a.port=21

FTP = ftplib.FTP()

print '[+] Connecting to host %s at port %d...' % (a.host, a.port),
sys.stdout.flush()
try:
    FTP.connect(a.host, a.port)
    print('OK.')
except:
    print('failed. Please check if the provided IP address/hostname and port are correct.')
    sys.exit(1)

print '[+] Logging in as user %s...' % (a.user),
sys.stdout.flush()
try:
    FTP.login(a.user, a.password)
    print('OK.')
except:
    FTP.quit()
    print('failed. Please check the provided username and password.')
    sys.exit(1)

print('[+] Welcome. Type help or ? to get started.\n')

while True:
    try:    
        prompt = raw_input('%s@%s:%s$ ' % (a.user, a.host, FTP.pwd())).strip('\r\n')
    except ftplib.error_perm, e:
        prompt = raw_input('%s@%s$ ' % (a.user, a.host)).strip('\r\n')
        no_pwd = True

    args = prompt.split(' ')

    cmd = args[0]

    if cmd == 'cd':
        if len(args) >= 2:
            _cd(' '.join(args[1:]))
        else:
            print('Syntax: cd <path>\n')
    elif cmd in ['dir', 'l', 'll', 'ls']:
        _ls()
    elif cmd == 'get':
        if len(args) == 2:
            _get(args[1], args[1])
        elif len(args) >= 3:
            _get(args[1], args[2])
        else:
            print('Syntax: get <remote_filename> [local_filename]\n')
    elif cmd == 'put':
        if len(args) == 2:
            _put(args[1], args[1])
        elif len(args) >= 3:
            _put(args[1], args[2])
        else:
            print('Syntax: put <local_filename> [remote_filename]\n')
    elif cmd == 'pwd':
        if no_pwd:
            print('%s: Command not implemented\n' % cmd)
        else:
            _pwd()
    elif cmd in ['help', '?']:
        if len(args) >= 2:
            _show_help(args[1])
        elif len(args) == 1:
            _show_help('')
        else:
            print('Syntax: help [command]\n')
    elif cmd in ['del', 'rm']:
        if len(args) >= 2:
            _rm(args[1])
        else:
            print('Syntax: rm <filename>\n')
    elif cmd in ['bye', 'exit', 'quit']:
        print('Bye.')
        break
    elif cmd in ['mkdir', 'md']:
        if len(args) >= 2:
            _mkdir(' '.join(args[1:]))
        else:
            print('Syntax: mkdir <directory_name>\n')
    elif cmd in ['rmdir', 'rd']:
        if len(args) >= 2:
            _rmdir(' '.join(args[1:]))
        else:
            print('Syntax: rmdir <directory_name>\n')
    elif cmd == '':
        continue
    else:
        print('%s: Command not found\n' % cmd)

try:
    FTP.quit()
except:
    print('exit: Connection reset by peer\n')
