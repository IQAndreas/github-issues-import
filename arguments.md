---
layout: slate
permalink: arguments/index.html
title: Command Line Arguments
subtitle: Command Line Arguments
---

### <a id="usage"></a> Usage

```
gh-issues-import.py [-h] [--help]
                    (--all | --open | --closed | -i ISSUES [ISSUES ...])
                    [--config CONFIG | --no-config]
                    [-u USERNAME] [-p PASSWORD]
                    [-s SOURCE] [-t TARGET]
                    [--ignore-comments] [--ignore-milestone] [--ignore-labels]
                    [--issue-template ISSUE_TEMPLATE]
                    [--comment-template COMMENT_TEMPLATE]
                    [--pull-request-template PULL_REQUEST_TEMPLATE]
```

### <a id="required-arguments"></a> Required arguments

At least one of the following is required:

```
--all                 Import all issues, regardless of state.
--open                Import only open issues.
--closed              Import only closed issues.
--issues ISSUES [ISSUES ...]
                      The list of issues to import. Can be abbreviated as `-i`.
```

Alternatively, the follwing flag should be used to display the help message and list of arguments, and then exit the program without doing anything.

```
-h, --help            show this help message and exit
```

### <a id="optional-arguments"></a> Optional arguments

For examples of config files, see [`config.ini.sample`](https://github.com/IQAndreas/github-issues-import/blob/master/config.ini.sample) or [`config-enterprise.ini.sample`](https://github.com/IQAndreas/github-issues-import/blob/master/config-enterprise.ini.sample) in the main repository.

```
--config CONFIG       The location of the config file (either absolute, or
                      relative to the current working directory). Defaults
                      to `config.ini` found in the same folder as this
                      script.
--no-config           No config file will be used, and the default
                      `config.ini` will be ignored. Instead, all settings
                      are either passed as arguments, or (where possible)
                      requested from the user as a prompt.
```

#### <a id="authentication"></a> Authentication

Note that if you want to use a different username/password combination for the source and target repositories, please use a config file instead.

```
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
                      copied from. Should be in the format `user/repository`.
-t TARGET, --target TARGET
                      The destination repository which the issues should be
                      copied to. Should be in the format `user/repository`.
```

#### <a id="other-options"></a> Other options

```
--ignore-comments     Do not import comments in the issue.
--ignore-milestone    Do not import the milestone attached to the issue.
--ignore-labels       Do not import labels attached to the issue.

--issue-template ISSUE_TEMPLATE
                      Specify a template file for use with issues.
--comment-template COMMENT_TEMPLATE
                      Specify a template file for use with comments.
--pull-request-template PULL_REQUEST_TEMPLATE
                      Specify a template file for use with pull requests.
```

