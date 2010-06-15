#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from mediacore.config.environment import load_batch_environment

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-d', '--dump', dest='dump_to', help='Dump the selected tables to OUTPUT_FILE', metavar='OUTPUT_FILE')
    parser.add_option('-r', '--read', dest='read_from', help='Update the database from the dump in INPUT_FILE', metavar='INPUT_FILE')
    parser.add_option('-i', '--ini', dest='ini_file', help='Specify the .ini file to read pylons settings from.', default='deployment.ini', metavar='INI_FILE')
    parser.add_option('--ini-path', dest='ini_path', help='Relative path to the .ini file.', default='../..', metavar='INI_PATH')
    parser.add_option('--debug', action='store_true', dest='debug', help='Write debug output to STDOUT.', default=False)
    options, args = parser.parse_args()
    return parser, options, args

DEBUG = False
if __name__ == "__main__":
    parser, options, args = parse_options()
    DEBUG = options.debug
    load_batch_environment(options.ini_path, options.ini_file)

# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import os
import sys
import select
import shutil
import commands
import subprocess
from pylons import config
from webob.exc import HTTPNotFound
from mediacore.model.meta import DBSession
from mediacore.model import *
from mediacore.lib import helpers

database = 'mediacore'
user = 'root'
password = ''
mysqldump_executable = 'mysqldump5'
mysql_executable = 'mysql5'
tables = [
    'tags',
    'settings',
    'podcasts',
    'categories',
    'media',
    'comments',
    'media_categories',
    'media_files',
    'media_tags',
]

# Data directories:
m_img_dir = config['image_dir'] + os.sep + Media._thumb_dir
p_img_dir = config['image_dir'] + os.sep + Podcast._thumb_dir
media_dir = config['media_dir']
deleted_dir = config.get('deleted_files_dir', '')
if deleted_dir:
    m_deleted_dir = deleted_dir + os.sep + 'media'
    p_deleted_dir = deleted_dir + os.sep + 'podcasts'

def poll_for_content(file_descriptor, timeout=0):
    ready = select.select([file_descriptor], [], [], timeout)[0]
    return ready and ready[0] == file_descriptor

def dump_backup_file(filename):
    # The tables we want to save.
    # In an order that will let them be created without Foreign Key problems.
    dump_cmd = "%s --user=%s --password=%s --compact %s %s" % (
        mysqldump_executable, user, password, database, " ".join(tables)
    )
    perl_cmd = 'perl -p -e "s:\),\(:\),\\n\(:g"'
    exc_string = "%s | %s" % (dump_cmd, perl_cmd)
    if DEBUG:
        print "Executing:"
        print "\t" + exc_string
        print ""
    status, output = commands.getstatusoutput(exc_string)

    try:
        f = open(filename, "w")
        f.write(output)
        f.close()
        output = "Success writing to file: %s" % filename
    except:
        output = "Error writing to file: %s" % filename
        status = 1

    return status, output


def restore_backup_file(filename):
    # Prepare the statements to lock, unlock, and drop all of the tables
    lock_stmt =  "START TRANSACTION;"
    disable_keys_stmt = "SET FOREIGN_KEY_CHECKS=0;"
    enable_keys_stmt = "SET FOREIGN_KEY_CHECKS=1;"
    commit_stmt = "COMMIT;"
    rollback_stmt = "ROLLBACK;"
    drop_stmt = "\n".join([
        'DROP TABLE IF EXISTS %s;' % t for t in tables
    ])

    # Prepare the statements to create tables + keys + load data
    print "Loading new data from %s..." % filename
    try:
        f = open(filename)
        file_input = f.read()
        f.close()
    except Exception, e:
        return 1, "Error reading data from %s" % filename
    print "Loaded data."

    # Put all the SQL in order in one big string.
    input = "\n".join((
        lock_stmt,
        disable_keys_stmt,
        drop_stmt,
        file_input,
        enable_keys_stmt,
    ))

    # Prepare the command to execute MySQL
    cmd_args = [
        mysql_executable,
        "--user=%s" % user,
        "--password=%s" % password,
        "--force", # Don't quit if a syntax error is encountered
        database,
    ]
    print "Executing:"
    print "\t" + " ".join(cmd_args)
    # Run mysql and feed it the SQL as STDIN
    process = subprocess.Popen(
        cmd_args,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )
    stdoutdata, stderrdata = '', ''
    try:
        print "Sending input data..."
        if DEBUG:
            print "Sending MySQL commands via STDIN:"
            print "\t" + input.replace("\n","\n\t")
            print ""
        process.stdin.write(input)
        if poll_for_content(process.stderr, timeout=2):
            raise Exception('Error occurred.')

        print "Committing changes..."
        # Attempt to commit the changes.
        stdoutdata, stderrdata = process.communicate("\n"+commit_stmt)
        status = 0
    except Exception, e:
        print "Sending or comitting data failed :( Rolling back any changes."
        # Oh no! An Error occurred. Roll back the transaction.
        stdoutdata, stderrdata = process.communicate("\n"+rollback_stmt)
        status = 1

    output = ""
    if stdoutdata:
        output = "STDOUT:\n\t" + stdoutdata.replace("\n", "\n\t")
    if stderrdata:
        output += "\n\nSTDERR:\n\t" + stderrdata.replace("\n", "\n\t")

    return status, output


def remove_unnecessary_files():
    # Move all media files and thumbnail files into 'deleted' folder.
    # XXX: don't run if deleted_dir is not set!
    if not deleted_dir:
        return

    for media in DBSession.query(Media).all():
        file_paths = helpers.thumb_paths(media)
        for f in media.files:
            file_paths.append(f.file_path)
        helpers.delete_files(file_paths, 'media')

    for podcast in DBSession.query(Podcast).all():
        file_paths = helpers.thumb_paths(podcast)
        helpers.delete_files(file_paths, 'podcasts')


def restore_necessary_files():
    # Restore the appropriate media files and thumbnail files
    # for any media currently in the database.
    # Use the python models to do this.
    if not deleted_dir:
        return

    filename_pairs = []
    for media in DBSession.query(Media).all():
        for thumb in helpers.thumb_paths(media):
            filename_pairs.append((
                thumb.replace(m_img_dir, m_deleted_dir),
                thumb
            ))
        for file in media.files:
            if file.file_path:
                filename_pairs.append((
                    file.file_path.replace(media_dir, m_deleted_dir),
                    file.file_path
                ))
    for podcast in DBSession.query(Podcast).all():
        for thumb in helpers.thumb_paths(podcast):
            filename_pairs.append((
                thumb.replace(p_img_dir, p_deleted_dir),
                thumb
            ))

    for src, dest in filename_pairs:
        if os.path.exists(src):
            if DEBUG:
                print "Moving % to %" % (src, dest)
            shutil.move(src, dest)

def main(parser):
    if options.dump_to:
        status, output = dump_backup_file(options.dump_to)

    if options.read_from:
        remove_unnecessary_files()
        status, output = restore_backup_file(options.read_from)
        DBSession.commit() # Create a new transaction, to reload the tables for
        restore_necessary_files()

    if not options.dump_to and not options.read_from:
        parser.print_help()
        print ""
        status, output = 1, 'Incorrect or insufficient arguments provided.\n'

    # print output and exit
    sys.stdout.write(output.strip())
    print ""
    if status == 0:
        print "Operation completed successfully."
    else:
        print "Error occurred in operation. You can use the --debug flag for more information."
    print ""
    sys.exit(status)

if __name__ == '__main__':
    main(parser)
