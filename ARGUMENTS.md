
###GitHub Issues Import

Import issues from one GitHub repository into another.

#### Usage

```
gh-issues-import.py [-h] [--config CONFIG] [-u USERNAME] [-p PASSWORD]
                         [-s SOURCE] [-t TARGET] [--ignore-comments]
                         [--ignore-milestone] [--ignore-labels]
                         [issues [issues ...]]
```

#### Positional arguments:

```
issues                The list of issues to import. If no issue ID is
                      provided, all open issues will be imported.
```

#### Optional arguments:

```
-h, --help            show this help message and exit

--config CONFIG       The location of the config file (either absolute, or
                      relative to the current working directory). Defaults
                      to `config.ini` found in the same folder as this
                      script.

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

