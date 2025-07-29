#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Code generator for python runtime library
'''

from os.path import basename, normpath
from pathlib import Path
from typing import Dict
from dmtgen.common.package import Package
from .generators.runtime_generator import RuntimeGenerator


def generate(input_dir: Path, output_dir: Path, config: Dict):
    """Generate typescript library based on DMT models"""
    package = Package(input_dir, None, config)
    gen_root = Path(__file__).resolve().parent
    folder = basename(normpath(input_dir))
    package_name = folder
    generator = RuntimeGenerator(gen_root, package_name, output_dir, package)
    generator.generate_package(config)
