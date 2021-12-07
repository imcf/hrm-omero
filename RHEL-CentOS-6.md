# CentOS 6 / RHEL 6

**NOTE:** they are EOL since 2020-11-30, please consider upgrading!

As we know that sometimes upgrading this is not easily doable due to dependencies,
hardware support or whatever reason - so here are instructions to make the connector
work on that old distribution.

We recommend to use [pyenv] for installing *Python 3.6*. In case you don't want
*pyenv* to mess with your system setup, you can simply ask it to install that version
somewhere and then only create a *virtual environment* from it using the `--copies`
flag - this will result in a standalone setup not affecting anything else on the system.

```bash
# install the build-time requirements for Python 3.6 and Java 1.8 for Bio-Formats
sudo yum install openssl-devel bzip2-devel readline-devel gcc-c++ java-1.8.0-openjdk

# get pyenv and put it into your home directory or wherever you prefer it to be
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# activate pyenv *FOR THIS SHELL ONLY* (needs to be done whenever you want to use it)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# ask pyenv to install Python 3.6.15 (will end up in "~/.pyenv/versions/3.6.15/")
pyenv install 3.6.15  # takes a bit (compiling...)

# define the target path for the virtual environment:
HRM_OMERO_VENV="/opt/venvs/hrm-omero"

# create a bare, stand-alone Python 3.6 virtual environment:
~/.pyenv/versions/3.6.15/bin/python -m venv --copies $HRM_OMERO_VENV
```

From here on follow the generic installation instructions.

[pyenv]: https://github.com/pyenv/pyenv