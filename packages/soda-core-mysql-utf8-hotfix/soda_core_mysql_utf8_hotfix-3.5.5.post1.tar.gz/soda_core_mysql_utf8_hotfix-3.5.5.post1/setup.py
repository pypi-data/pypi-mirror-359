#!/usr/bin/env python

from setuptools import find_namespace_packages, setup

package_name = "soda-core-mysql-utf8-hotfix"
package_version = "3.5.5.post1"
description = "Soda Core MySQL Package - UTF8 Charset Hotfix"

long_description = """
# Soda Core MySQL Package - UTF8 Charset Hotfix

⚠️ **WARNING: This is an unofficial temporary hotfix for the [soda-core-mysql](https://pypi.org/project/soda-core-mysql/) package.**

**This is NOT the official version. Do not use on production environments.**

**This package will be deleted once the fix is applied to the official package.**

## Known Issue

If you are running MySQL versions lower than 5.5.3, the Python connector version (8.0.30)
will try to alias utf8 to utf8mb4 (which obviously doesn't exist yet for versions less than 5.5.3)
as stated in its release notes.

This may result in the error: `Character set 'utf8' unsupported`

## Recommendations

- Please ensure you are using MySQL 5.5.3 or higher
- If you must use older MySQL versions, consider using an older version of the mysql-connector-python package
"""

requires = [
    "soda-core==3.5.5",
    "mysql-connector-python==8.0.33",
]
# TODO Fix the params
setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/addiewan/soda-core",
    install_requires=requires,
    packages=find_namespace_packages(include=["soda*"]),
)
