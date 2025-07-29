# SPDX-FileCopyrightText: 2025-present Guille on a Raspberry pi <guilleleiratemes@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ..templates import package, builder, gpl_license
import os
import json
import datetime

def new(name):
    year = datetime.datetime.now().year
    os.mkdir(name)
    os.chdir(name)
    copyright_header = f"{name} Copyright (c) {year}-present [YOU] [YOUR_EMAIL]"
    with open("package.json", "w") as f:
        json.dump(package.template, f)
    os.mkdir("src")
    with open("builder.zl", "w") as f:
        f.write(builder.template)
    with open("LICENSE.txt", "w") as f:
        f.write(gpl_license.template)
        f.write(copyright_header)
    with open("README.md", "w") as f:
        f.write(f"""# {name}""")
