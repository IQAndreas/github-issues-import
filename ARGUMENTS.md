###GitHub Issues Import

Import issues from one GitHub repository into another.

#### Usage

```
gh-issues-import.py [-h] [--config CONFIG] [-u USERNAME] [-p PASSWORD]
                         [-s SOURCE] [-t TARGET]
                         [--ignore-comments] [--ignore-milestone] [--ignore-labels]
                         (--all | --open | --closed | --issues ISSUES [ISSUES ...])
```

#### Required arguments:

At least one of the following is required:

```
--all                 Import all issues, regardless of state.
--open                Import only open issues.
--closed              Import only closed issues.
--issues ISSUES [ISSUES ...]
                      The list of issues to import.
```

Alternatively, the follwing flag should be used to display the help message and list of arguments, and then exit the program without doing anything.

```
-h, --help            show this help message and exit
```

#### Optional arguments:

```
--config CONFIG       The location of the config file (either absolute, or
                      relative to the current working directory). Defaults
                      to `config.ini` found in the same folder as this
                      script; use `--no-config` if you want the script 
                      to even ignore the default file.

-u USERNAME, --username USERNAME
                      The username of the account that will create the new
                      issues. The username will not be stored anywhere if
                      passed in as an argument.
-p PASSWORD, --password PASSWORD
                      The password (in plaintext) of the account that will
                      create the new issues. The password will not be stored
                      anywhere if passed in as an argument.

-s SOURCE, --source SOURCE
                      The source repository which the issues should be
                      copied from. Should be in the format
                      `user/repository`.
-t TARGET, --target TARGET
                      The destination repository which the issues should be
                      copied to. Should be in the format `user/repository`.

--ignore-comments     Do not import comments in the issue.
--ignore-milestone    Do not import the milestone attached to the issue.
--ignore-labels       Do not import labels attached to the issue.
```

