<!--
SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH

SPDX-License-Identifier: CC-BY-4.0
-->

# Elements HTTP Upload Uitility

[![CI](https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload/badges/main/pipeline.svg)](https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload/-/pipelines?page=1&scope=all&ref=main)
[![Code coverage](https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload/badges/main/coverage.svg)](https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload/-/graphs/main/charts)
<!-- TODO: uncomment the following line when the package is registered at https://readthedocs.org -->
<!-- [![Docs](https://readthedocs.org/projects/elements-http-upload/badge/?version=latest)](https://elements-http-upload.readthedocs.io/en/latest/) -->
[![Latest Release](https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload/-/badges/release.svg)](https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload)
<!-- TODO: uncomment the following line when the package is published at https://pypi.org -->
<!-- [![PyPI version](https://img.shields.io/pypi/v/elements-http-upload.svg)](https://pypi.python.org/pypi/elements-http-upload/) -->
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
<!-- TODO: uncomment the following line when the package is registered at https://api.reuse.software -->
<!-- [![REUSE status](https://api.reuse.software/badge/codebase.helmholtz.cloud/hcdc/elements/elements-http-upload)](https://api.reuse.software/info/codebase.helmholtz.cloud/hcdc/elements/elements-http-upload) -->


A small convenience command-line utility to upload files via HTTP to an elements instance

The command-line utility provided by this package has been tested with an [ELEMENTS](https://elements.tv/) installation
of v25.1.2. It mimics the upload of the web interface when uploading a file via HTTP(S). The file is split into
chunks and uploaded one by one.

**Note that the authors of this package are not affiliated in any kind with syslink GmbH (the copyright holders of elements).**

## Installation

Install this package in a dedicated python environment via

```bash
python -m venv venv
source venv/bin/activate
pip install elements-http-upload
```

To use this in a development setup, clone the [source code][source code] from
gitlab, start the development server and make your changes::

```bash
git clone https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload
cd elements-http-upload
python -m venv venv
source venv/bin/activate
make dev-install
```

More detailed installation instructions my be found in the [docs][docs].


[source code]: https://codebase.helmholtz.cloud/hcdc/elements/elements-http-upload
[docs]: https://elements-http-upload.readthedocs.io/en/latest/installation.html

## Command-line usage

To upload a file, run

```bash
elements-http-upload -t <api-token> -H https://<your-elements-installation> <local-file>:<remote-folder>/<remote-file>
```

An API token can be retrieved from the MAMS web interface by clicking your profile in the upper right corner and
selecting the *API* tab. For further instructions, please have a look into the [usage docs][usage docs].

[usage docs]: https://elements-http-upload.readthedocs.io/en/latest/usage.html

## Technical note

This package has been generated from the template
https://codebase.helmholtz.cloud/hcdc/software-templates/python-cli-package-template.git.

See the template repository for instructions on how to update the skeleton for
this package.


## License information

Copyright © 2025 Helmholtz-Zentrum hereon GmbH



Code files in this repository are licensed under the
Apache-2.0, if not stated otherwise
in the file.

Documentation files in this repository are licensed under CC-BY-4.0, if not stated otherwise in the file.

Supplementary and configuration files in this repository are licensed
under CC0-1.0, if not stated otherwise
in the file.

Please check the header of the individual files for more detailed
information.



### License management

License management is handled with [``reuse``](https://reuse.readthedocs.io/).
If you have any questions on this, please have a look into the
[contributing guide][contributing] or contact the maintainers of
`elements-http-upload`.

[contributing]: https://elements-http-upload.readthedocs.io/en/latest/contributing.html
