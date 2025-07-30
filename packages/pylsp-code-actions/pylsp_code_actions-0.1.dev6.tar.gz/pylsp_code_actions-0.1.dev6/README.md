<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# PyLSP Code Actions

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pylsp-code-actions)
![Code QA workflow status](https://github.com/DSD-DBS/pylsp-code-actions/actions/workflows/code-qa.yml/badge.svg)

Handy code actions for python-lsp-server

This is a plugin for `python-lsp-server` which adds a few handy code actions
that I always missed:

- [x] Flip comma or other operand
- [ ] Sort keyword arguments by name
- [ ] Order keyword arguments as in the called function
- [ ] Sort dict literal by keys
- [x] Generate docstring for function/method
- [ ] Add / Remove `Annotated[...]` around a type annotation

# Installation

Run the following command in the same venv as the server itself:

```sh
pip install pylsp-code-actions
```

If you are using neovim and mason, use:

```vim
:PylspInstall pylsp-code-actions
```

<sub>(I use neovim too btw. I also use Arch btw.)</sub>

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a
look at our [guidelines for contributors](CONTRIBUTING.md) for details. It also
contains a short guide on how to set up a local development environment.

# Licenses

This project is compliant with the
[REUSE Specification Version 3.0](https://git.fsfe.org/reuse/docs/src/commit/d173a27231a36e1a2a3af07421f5e557ae0fec46/spec.md).

Copyright DB InfraGO AG, licensed under Apache 2.0 (see full text in
[LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt))

Dot-files are licensed under CC0-1.0 (see full text in
[LICENSES/CC0-1.0.txt](LICENSES/CC0-1.0.txt))
