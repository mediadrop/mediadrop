#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from mediacore.lib.cli_commands import LoadAppCommand, load_app

_script_name = "Backup & Restore Script"
_script_description = """
Use this script to backup and restore the important tables from a MediaCore
deployment, and to restore the files associated with the data in those tables.
"""
DEBUG = False

if __name__ == "__main__":
    cmd = LoadAppCommand(_script_name, _script_description)
    cmd.parser.add_option('--dump',
        dest='dump_to',
        help='Dump the selected tables to OUTPUT_FILE',
        metavar='OUTPUT_FILE'
    )
    cmd.parser.add_option('--restore',
        dest='read_from',
        help='Update the database from the dump in INPUT_FILE',
        metavar='INPUT_FILE'
    )
    cmd.parser.add_option('--dump-files',
        dest='dump_files_dir',
        help="Back up the your thumbnails and locally stored media files to "\
             "DIR. DIR must be a directory that already exists. "\
             "WARNING: this flag will delete any existing files from DIR "\
             "before performing the backup!",
        metavar='DIR'
    )
    cmd.parser.add_option('--restore-files',
        dest='restore_files_dir',
        help="Restore the dumped thumbnails and media files from DIR to "\
             "MediaCore's configured storage locations. "\
             "WARNING: this flag will delete all files from its destination "\
             "directories before performing a restore!",
        metavar='DIR'
    )
    cmd.parser.add_option('--debug',
        action='store_true',
        dest='debug',
        help='Write debug output to STDOUT.',
        default=False
    )
    load_app(cmd)
    DEBUG = cmd.options.debug


# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import os
import sys
import select
import shutil
import commands
import subprocess
import urlparse
from pylons import config
from webob.exc import HTTPNotFound
from mediacore.model.meta import DBSession
from mediacore.model import *
from mediacore.lib import helpers
from mediacore.lib.thumbnails import thumb_paths
from mediacore.lib.compat import any
from mediacore.lib.uri import file_path


def is_executable(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

def find_executable(names):
    # Given a list of executable names, find the first one that is available
    # as an executable file, on the path.
    for name in names:
        fpath, fname = os.path.split(name)
        if fpath:
            # The given name is absolute.
            if is_executable(name):
                return name
        else:
            # Try to find the name on the PATH
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, name)
                if is_executable(exe_file):
                    return exe_file

    # Could not find it :(
    return None


# our database info
db_url = config['sqlalchemy.url'].replace('mysql://', 'http://') # to trick urlparse
db_info = urlparse.urlsplit(db_url)
db_user = db_info.username
db_pass = db_info.password
db_info = urlparse.urlparse(db_url)
db_name = db_info.path.strip('/')
mysqldump_executable = find_executable(['mysqldump5', 'mysqldump'])
mysql_executable = find_executable(['mysql5', 'mysql'])

# The tables we want to save.
tables = [
    'categories',
    'comments',
    'groups',
    'media',
    'media_fulltext',
    'permissions',
    'players',
    'podcasts',
    'settings',
    'settings_multi',
    'storage',
    'tags',
    'users',
    'groups_permissions',
    'media_categories',
    'media_files',
    'media_files_meta',
    'media_meta',
    'media_tags',
    'users_groups',
]

# Data directories:
m_img_dir = config['image_dir'] + os.sep + Media._thumb_dir
p_img_dir = config['image_dir'] + os.sep + Podcast._thumb_dir
media_dir = config['media_dir']
deleted_dir = config.get('deleted_files_dir', '')
if deleted_dir:
    m_deleted_dir = deleted_dir + os.sep + Media._thumb_dir
    p_deleted_dir = deleted_dir + os.sep + Podcast._thumb_dir

def poll_for_content(file_descriptor, timeout=0):
    # return a bool: after waiting for timeout seconds,
    #                does file_descriptor have anything waiting to be read?
    ready = select.select([file_descriptor], [], [], timeout)[0]
    return ready and ready[0] == file_descriptor

def dump_backup_file(filename):
    dump_cmd = '%s --user="%s" --password="%s" --compact %s %s' % (
        mysqldump_executable, db_user, db_pass, db_name, " ".join(tables)
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
    charset_stmt = "SET character_set_client=utf8;"
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
        charset_stmt,
        lock_stmt,
        disable_keys_stmt,
        drop_stmt,
        file_input,
        enable_keys_stmt,
    ))

    # Prepare the command to execute MySQL
    cmd_args = [
        mysql_executable,
        "--user=%s" % db_user,
        "--password=%s" % db_pass,
        "--force", # Don't quit if a syntax error is encountered
        db_name,
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
            # Has an error message been written to stderr after 2 seconds?
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

def empty_dir(dir):
    # delete all non-hidden files from dir
    files = [
        dir + os.sep + f
        for f in os.listdir(dir)
        if not f.startswith('.')
    ]
    for path in files:
        os.remove(path)

def backup_files(dump_dir):
    # Backup all files (media files, thumbs) referenced by an object in the DB
    # to the provided dump_dir.

    # TODO: display errors when file operations fail

    if dump_dir == '/':
        return 1, "Dump Files directory should never be the root directory, '/'"

    # normalize dirname
    dump_dir = dump_dir.rstrip(os.sep) + os.sep

    # These are the directories we will write to.
    media_thumb_dir = dump_dir + Media._thumb_dir
    podcast_thumb_dir = dump_dir + Podcast._thumb_dir
    media_files_dir = dump_dir + 'media_files'

    # Initialize our default paths to backup
    default_images = ['news.jpg', 'newm.jpg', 'newl.jpg']
    media_thumbs = [m_img_dir+os.sep+img for img in default_images]
    podcast_thumbs = [p_img_dir+os.sep+img for img in default_images]
    media_files = []

    # Add the media thumbs and media files
    for media in DBSession.query(Media).all():
        file_paths = [file_path(f) for f in media.files]
        media_files += [fp for fp in file_paths if fp]
        media_thumbs += thumb_paths(media).values()

    # Add the podcast thumbs
    for podcast in DBSession.query(Podcast).all():
        podcast_thumbs += thumb_paths(podcast).values()

    # Ensure the necessary directories exist.
    assert os.path.isdir(dump_dir)
    for subdir in (media_thumb_dir, media_files_dir, podcast_thumb_dir):
        if not os.path.exists(subdir):
            os.mkdir(subdir)
        assert os.path.isdir(subdir)
        empty_dir(subdir)

    # Copy over all of the files:
    sources_dests = (
        (media_thumbs, media_thumb_dir),
        (media_files, media_files_dir),
        (podcast_thumbs, podcast_thumb_dir),
    )
    for sources, dest_dir in sources_dests:
        for src in sources:
            if DEBUG:
                print "Copying %s to %s%s" % (src, dest_dir, os.sep)
            shutil.copy2(src, dest_dir)

    return 0,'%d thumbnails and %d media files successfully backed up' %\
            (len(media_thumbs) + len(podcast_thumbs), len(media_files))

def restore_files(restore_dir):
    # Restore all files from the provided restore_dir to their regular
    # locations within MediaCore (probably in the ./data directory)

    # TODO: display errors when file operations fail

    # normalize dirname
    restore_dir = restore_dir.rstrip(os.sep) + os.sep

    # These are the directories we will read from.
    media_thumb_dir = restore_dir + Media._thumb_dir
    podcast_thumb_dir = restore_dir + Podcast._thumb_dir
    media_files_dir = restore_dir + 'media_files'

    # Ensure the necessary directories exist.
    assert os.path.isdir(restore_dir)
    for subdir in (media_thumb_dir, media_files_dir, podcast_thumb_dir):
        assert os.path.isdir(subdir)

    source_dest_dirs = (
        (media_thumb_dir, m_img_dir),
        (media_files_dir, media_dir),
        (podcast_thumb_dir, p_img_dir),
    )
    counts = [0, 0, 0]
    i = -1
    for source_dir, dest_dir in source_dest_dirs:
        i += 1
        empty_dir(dest_dir)
        for f in os.listdir(source_dir):
            counts[i] += 1
            src = source_dir + os.sep + f
            dest = dest_dir + os.sep + f
            if DEBUG:
                print "Copying %s to %s" % (src, dest)
            shutil.copy2(src, dest)

    return 0,'%d thumbnails and %d media files successfully backed up' %\
            (counts[0]+counts[2], counts[1])

def main(parser, options):
    status = 0
    output = []

    if options.dump_to:
        s, o = dump_backup_file(options.dump_to)
        status += s
        output.append(o.strip())
        DBSession.commit() # Commit and start a new transaction

    if options.read_from:
        s, o = restore_backup_file(options.read_from)
        status += s
        output.append(o.strip())
        DBSession.commit() # Commit and start a new transaction

    if options.dump_files_dir:
        s, o = backup_files(options.dump_files_dir)
        status += s
        output.append(o.strip())

    if options.restore_files_dir:
        s, o = restore_files(options.restore_files_dir)
        status += s
        output.append(o.strip())

    if not any((options.dump_to, options.read_from,
                options.dump_files_dir, options.restore_files_dir)):
        parser.print_help()
        print ""
        status, output = 1, ['Incorrect or insufficient arguments provided.\n']

    # print output and exit
    sys.stdout.write("\n---\n".join(output))
    print ""
    if status == 0:
        print "Operation completed successfully."
    else:
        print "Error occurred in operation. You can use the --debug flag for more information."
    print ""
    sys.exit(status)

if __name__ == '__main__':
    main(cmd.parser, cmd.options)
