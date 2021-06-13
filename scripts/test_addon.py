#!/usr/bin/python3

# This file is part of PAINTicle.
#
# PAINTicle is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAINTicle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PAINTicle.  If not, see <http://www.gnu.org/licenses/>.

import blender_addon_tester
import os
import sys

import argparse

parser = argparse.ArgumentParser(description='Unit test starter for painticle blender addon.')
parser.add_argument('--cov', help="Perform code coverage",
                    action='store_true')
parser.add_argument('--dbg', help="When debugging don't capture at all",
                    action='store_true')
parser.add_argument('--ui', help="Allow some UI related tests, by not running blender in -b mode",
                    action='store_true')
parser.add_argument('--test', help="Specify a single test to run", default="")
parser.add_argument('--rev', help="Specify the blender revision for the test environment (default=2.92)",
                    default="2.92")
args = parser.parse_args()

script_dir = os.path.dirname(os.path.realpath(__file__))
tests_results_path = os.path.join(script_dir, "..", "tests_results")
tests_path = os.path.join(script_dir, "..", "tests") if args.test == "" else os.path.abspath(args.test)
addon_path = os.path.join(script_dir, "..", "build", "out", "painticle")

os.chdir(tests_results_path)

# Passing the cache dir through the config doesn't work, due to a strange test for unknown keys.
# If the user doesn't override the cache location, constrain the caching inside of our addon's directory.
if 'BLENDER_CACHE' not in os.environ:
    os.environ['BLENDER_CACHE'] = os.path.join(tests_results_path, "blender_cache")

# Setup a local config and script installation environment to not pollute the user's one
os.environ['BLENDER_USER_CONFIG'] = os.path.join(os.environ['BLENDER_CACHE'], "local_config_"+args.rev)

config = {
    "run_in_window": args.ui,
    "tests": tests_path
}

if args.cov:
    config["coverage"] = args.cov
    config["pytest_args"] = "--cov-config="+os.path.join(script_dir, "coveragerc")
else:
    config["pytest_args"] = "--capture=no" if args.dbg else "-rx"

try:
    exit_value = blender_addon_tester.test_blender_addon(addon_path=os.path.abspath(addon_path),
                                                         blender_revision=args.rev, config=config)
except Exception as e:
    print(e)
    exit_value = 1

sys.exit(exit_value)
