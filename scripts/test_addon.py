#!/usr/bin/python3

import blender_addon_tester
import os

import argparse

parser = argparse.ArgumentParser(description='Unit test starter for particle_paint blender addon.')
parser.add_argument('--cov', help="Perform code coverage", action='store_true')
parser.add_argument('--dbg', help="When debugging don't capture at all", action='store_true')
parser.add_argument('--rev', help="Specify the blender revision for the test environment (default=2.92)", default="2.92")
args = parser.parse_args()

script_dir = os.path.dirname(os.path.realpath(__file__))
tests_results_path = os.path.join(script_dir, "..", "tests_results")
addon_path = os.path.join(script_dir, "..", "particle_paint")

os.chdir(tests_results_path)

# Passing the cache dir through the config doesn't work, due to a strange test for unknown keys.
# If the user doesn't override the cache location, constrain the caching inside of our addon's directory.
if not 'BLENDER_CACHE' in os.environ:
    os.environ['BLENDER_CACHE'] = os.path.join(tests_results_path, "blender_cache")

config = { }
if args.cov:
    config["coverage"] = args.cov
    config["pytest_args"] = "--cov-config="+os.path.join(script_dir, "coveragerc")
else:
    config["pytest_args"] = "--capture=no" if args.dbg else "-rx"

blender_addon_tester.test_blender_addon(addon_path=os.path.abspath(addon_path), blender_revision=args.rev, config=config )
