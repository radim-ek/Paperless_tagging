#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from paperless_sync.sync import run_dir_sync

if __name__ == "__main__":
    run_dir_sync()
