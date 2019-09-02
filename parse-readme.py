#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Richard Hughes <richard@hughsie.com>
# Licensed under the GNU General Public License Version or later

from __future__ import print_function
import sys

def main():
    if len(sys.argv) != 3:
        print("usage: %s README.txt \"header to match\"" % sys.argv[0])
        return 1

    # open file
    f = open(sys.argv[1])
    in_section = False
    in_table = False
    pids = []
    for line in f.readlines():

        # find the right data table
        if line.find(sys.argv[2]) != -1:
            in_section = True
            continue
        if not in_section:
            continue

        # remove Windows and Linux line endings
        line = line.replace('\r', '')
        line = line.replace('\n', '')

        # end of section
        if len(line) > 0 and not line.startswith('    '):
            in_section = False
            in_table = False
            continue

        # empty line
        if len(line) == 0:
            continue

        # skip the header
        if line.startswith('    ---'):
            in_table = True
            continue
        if not in_table:
            continue

        # get name
        pid = int(line[42:46], 16)
        if not pid in pids:
            pids.append(pid)

    # output
    for pid in pids:
        vid = 0x10de
        print("pci:v%08Xd%08Xsv*sd*bc*sc*i*" % (vid, pid))

if __name__ == "__main__":
    main()
