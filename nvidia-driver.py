#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Simone Caronni <negativo17@gmail.com>
# Licensed under the GNU General Public License Version or later

import sys

def main():
    if len(sys.argv) != 2:
        print("usage: %s README.txt" % sys.argv[0])
        return 1

    f = open(sys.argv[1])
    in_section = False
    in_table = False
    pids = []
    sections = ["NVIDIA GEFORCE GPUS", "NVIDIA RTX/QUADRO GPUS", "NVIDIA NVS GPUS", "NVIDIA TESLA GPUS", "NVIDIA GRID GPUS"]
    for section in sections:

        for line in f.readlines():

            # Find the right data tables
            if line.find(section) != -1:
                in_section = True
                continue
            if not in_section:
                continue

            # Remove Windows and Linux line endings
            line = line.replace('\r', '')
            line = line.replace('\n', '')

            # End of section
            if len(line) > 0 and not line.startswith(' '):
                in_section = False
                in_table = False
                continue

            if len(line) == 0:
                continue

            # Skip the header
            if line.startswith(' ---'):
                in_table = True
                continue
            if not in_table:
                continue

            # PCI ID
            pid = int(line[50:54], 16)
            if not pid in pids:
                pids.append(pid)

    for pid in pids:
        vid = 0x10de
        print("pci:v%08Xd%08Xsv*sd*bc*sc*i*" % (vid, pid))

if __name__ == "__main__":
    main()
