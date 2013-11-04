#!/usr/bin/env python

keywords = [
    'TODO',
    'TOFIX',
    'FIXME',
    'HACK',
    'XXX',
    'WARN',
]
import os
grep_cmd = """grep -ERn "%s" """ % ("|".join(keywords))
files_and_dirs = [
    'batch-scripts',
    'deployment-scripts',
    'mediadrop',
    'plugins',
    'setup*',
]
exclude_files_and_dirs = [
    'batch-scripts/find_todos.py',
    'mediadrop/public/scripts/third-party/',
    'mediadrop/lib/xhtml/htmlsanitizer.py',
    'mediadrop/public/scripts/mcore-compiled.js',
]

IN, MULT = 1, 2

# File extensions for files that share comment styles.
c_like_files = ['c', 'h', 'java', 'cpp']
html_files = ['xml', 'html', 'xhtml', 'htm']
js_files = ['js']
css_files = ['css']
python_files = ['py']
sql_files = ['sql']
ini_files = ['ini', 'ini_tmpl']

# multiline comment beginning/ending strings
# mapped to the filetypes associated with them.
multiline = {
    ('<!--!', '-->'): html_files + python_files,
    ('"""', '"""'): python_files,
    ('/*', '*/'): c_like_files + js_files + css_files + html_files,
}

# inline comment beginning strings
# mapped to the filetypes associated with them.
inline = {
    '#': python_files + ini_files,
    '//': c_like_files + js_files + html_files,
    '--': sql_files,
}

def get_beginning(lines, line_no, filename):
    # Find the beginning of the enclosing comment block, for the
    # comment on the given line
    line_offset = line_no
    while line_offset >= 0:
        line = lines[line_offset]

        for begin, end in multiline:
            if not any(map(filename.endswith, multiline[(begin, end)])):
                continue
            char_offset = line.find(begin)
            if char_offset >= 0:
                return begin, end, line_offset, char_offset, MULT

        for begin in inline:
            if not any(map(filename.endswith, inline[begin])):
                continue
            char_offset = line.find(begin)
            if char_offset >= 0:
                return begin, None, line_offset, char_offset, IN

        line_offset -= 1
    return None, None, None, None, None

def get_ending(lines, begin, end, begin_line, begin_char, type):
    # Find the ending of the enclosing comment block, given a
    # description of the beginning of the block
    end_line = begin_line
    end_char = 0

    if type == MULT:
        while (end_line < len(lines)):
            start = 0
            if end_line == begin_line:
                start = begin_char + len(begin)
            end_char = lines[end_line].find(end, start)
            if end_char >= 0:
                break
            end_line += 1
        end_line += 1
    elif type == IN:
        while (end_line < len(lines)):
            start = 0
            if end_line == begin_line:
                start = lines[end_line].index(begin)
            if not lines[end_line][start:].strip().startswith(begin):
                break
            end_line += 1

    return end_line, end_char

def get_lines(lines, line_no, filename):
    # FIRST, GET THE ENTIRE CONTAINING COMMENT BLOCK
    begin, end, begin_line, begin_char, type = get_beginning(lines, line_no, filename)
    if (begin,end) == (None, None):
        return None # false alarm, this isn't a comment at all!
    end_line, end_char = get_ending(lines, begin, end, begin_line, begin_char, type)
    lines = map(lambda line: line.strip(), lines[begin_line:end_line])
    # "lines" NOW HOLDS EVERY LINE IN THE CONTAINING COMMENT BLOCK

    # NOW, FIND ONLY THE LINES IN THE SECTION WE CARE ABOUT
    offset = line_no - begin_line
    lines = lines[offset:]
    size = 1
    while size < len(lines):
        line = lines[size].strip().lstrip(begin)
        if line == "":
            break
        size += 1

    return lines[:size]

# Keep track of how many of each keyword we see
counts = { }
for k in keywords:
    counts[k] = 0

# Populate a dict of filename -> [lines of interest]
matched_files = {}
for x in files_and_dirs:
    cmd = grep_cmd + x
    result = os.popen(cmd)
    for line in result.readlines():

        if line.startswith('Binary file'):
            # ignore binary files
            continue

        if any(map(line.startswith, exclude_files_and_dirs)):
            # don't include the specifically excluded dirs
            continue

        file, line_no, rest = line.split(":", 2)

        for k in counts:
            # keep track of how many of each keyword we see
            if k in rest:
                counts[k] += 1

        # Add this entry to the dict.
        if file not in matched_files:
            matched_files[file] = []
        matched_files[file].append(int(line_no))

# Iterate over each filename, printing the found
# todo blocks.
for x in sorted(matched_files.keys()):
    line_nos = matched_files[x]
    f = open(x)
    lines = f.readlines()
    f.close()
    output = ["\nFILE: %s\n-----" % x]
    for i, num in enumerate(line_nos):
        curr_line = line_nos[i]-1
        next_line = None
        if (i+1) < len(line_nos):
            next_line = line_nos[i+1]-1

        todo_lines = get_lines(lines, curr_line, x)
        if not todo_lines:
            continue

        if next_line is not None:
            # ensure that the current 'todo' item doesn't
            # overlap with the next 'todo' item.
            max_length = next_line - curr_line
            todo_lines = todo_lines[:max_length]

        output.append("line: %d\n%s\n" % (num, "\n".join(todo_lines)))

    if len(output) > 1:
        for chunk in output:
            print chunk

# Print our counts
for k in counts:
    print k, counts[k]
