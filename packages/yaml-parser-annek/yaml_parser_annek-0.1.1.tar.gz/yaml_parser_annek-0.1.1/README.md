# `ypa`

A CLI for parsing yaml files.

You must set YPA_IMPORT_DIR and YPA_EXPORT_DIR or define them in a .env file.

Example:

YPA_IMPORT_DIR=&quot;/my-yaml-files&quot;

YPA_EXPORT_DIR=&quot;/inventory/host_vars&quot;

**Usage**:

```console
$ ypa [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `get-machine-details`: Get details for Machines from a YAML file.
* `write-hostvar-files`: Export machine details to a file.

## `ypa get-machine-details`

Get details for Machines from a YAML file.

Arguments:

filename: The path to the YAML file.

**Usage**:

```console
$ ypa get-machine-details [OPTIONS] FILENAME
```

**Arguments**:

* `FILENAME`: [required]

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `ypa write-hostvar-files`

Export machine details to a file.

Arguments:

import_filename: The path to the YAML file to import.

**Usage**:

```console
$ ypa write-hostvar-files [OPTIONS] IMPORT_FILENAME
```

**Arguments**:

* `IMPORT_FILENAME`: [required]

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.
