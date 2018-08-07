#     Copyright 2018 Will Bengtson
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
import re
import ast
import os.path
import sys
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('trailblazer/__about__.py', 'rb') as f:
    TRAILBLAZER_VERSION = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

# When executing the setup.py, we need to be able to import ourselves.  This
# means that we need to add the src/ directory to the sys.path

sys.path.insert(0, ROOT)

install_requirements = [
    'boto3>=1.5.34',
    'click==6.7',
    'click-log==0.2.1',
    'PyYAML==3.12'
]

setup(
    name='trailblazer-aws',
    version=TRAILBLAZER_VERSION,
    long_description="CloudTrail enumeration and AWS attack platform",
    packages=find_packages(),
    install_requires=install_requirements,
    entry_points={
        'console_scripts': [
            'trailblazer = trailblazer.cli:cli',
        ],
    }
)