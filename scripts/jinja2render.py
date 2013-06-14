#!/usr/bin/env python
"""

Produce output from a template and data file
Top row of data.csv has tags to be replaced in template.

"""

import sys
import os
from optparse import OptionParser
from jinja2 import Environment, FileSystemLoader

def main():
    parser = OptionParser(usage="usage: %prog [options] template.jinja2 outfile")
    (options,args) = parser.parse_args()
    try:
        templin = open (args[0],'r').read()
    except:
        parser.print_help()
        sys.exit(1)
    TEMPLATE_DIR = os.path.dirname(args[0])
    BASENAME = os.path.basename(args[0])

    j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),trim_blocks=True)
    output=j2_env.get_template(BASENAME).render()

    sys.stdout.write(output)

if __name__ == "__main__":
    main()

