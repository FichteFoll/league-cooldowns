#!/usr/bin/env python3.5

import sys
from . import main

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
