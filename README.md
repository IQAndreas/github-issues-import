
### GitHub Issues Import ###

This Python script allows you to import issues and pull requests from one repository to another; works even for private repositories, and if the two repositories are not related to each other in any way.

Fork of one of the tools by [Max Korenkov](https://github.com/mkorenkov) separated from its original location at [`mokorenkov/tools`](https://github.com/mkorenkov/tools).

#### Usage ####

Rename `config.ini.sample` to `config.ini`, and edit the fields to match your login info and repository info. _NOTE: If you want to use a different credentials for the source and target repositories, please see the below section for Enterprise Users._ Store the config file in the same folder as the `gh-issues-import.py` script, or store it in a different folder, using the `--config <file>` option to specify which config file to load in.

**Warning:** The password is stored in plain-text, so avoid storing the config file in a public repository. To avoid this, you can instead pass the username and/or password as arguments by using the `-u <username>` and `-p <password>` flags respectively. If the username or password is not passed in from either of these locations, the user will be prompted for them when the script runs.
 
Run the script with the following command to import all open issues into the repository defined in the config:

```
 $ python3 gh-issues-import.py --open
```

If you want to import all issues (including the closed ones), use `--all` instead of `--open`. Closed issues will still be open in the target repository, but titles will begin with `[CLOSED]`.

Or to only import specific issues, run the script and include the issue numbers of all issues you wish to import (can be done for one or several issues, and will even include closed issues):

```
 $ python3 gh-issues-import.py --issues 25 26 29
```

Some config options can be passed as arguments. For a full list, see [ARGUMENTS.md](https://github.com/IQAndreas/github-issues-import/blob/docs/ARGUMENTS.md), or run the script using the `--help` flag.

#### Enterprise Users ####

If you are using [GitHub for Enterprise](https://enterprise.github.com/), thanks to the help of [Joshua Rountree](https://github.com/joshuairl), there is support for that. These changes also allow you to specify a different username and password for the source and target repositories, even if both of them are hosted on GitHub.

Use the [`config-enterprise.ini.sample`](config-enterprise.ini.sample) file as a template (renaming it to `config.ini`, or using the `--config <file>` flag). The command line options `--username` and `--password` do not allow you to specify which repository the credentials apply to, so unless you use the same credentials for both servers, a config file _must_ be used.

#### Result ####

Every issue imported will create a new issue in the target repository. Remember that the ID of the issue in the new repository will most likely not be the same as the ID of the original issue. Keep this in mind when writing commit messages such as _"Closes #25"_.

If the issue is a pull request, this will be indicated on the issue, and a link to the code will be provided. However, it will be treated as a new issue in the target repository, and **not** a pull request. Pulling in the suggested code into the repository will need to be done manually.

Any comments on the issue will be imported, however, the author of all imported comments will be the account specified in the config. Instead, a link and header is provided for each comment indicating who the original author was and the original date and time of the comment. Any subsequent comments added to the issue after it has been imported into the target repository will not be included.

Labels and milestones attached to the issue will be imported and added to the target repository if they do not already exist there. If the label or milestone with the same name already exists, the issue will point to the existing one, and any difference in the description or other details will be ignored.

If allowed by GitHub's policies, it may be a good idea to use a "neutral" account to import the issues and issue comments to avoid imported comments from getting mixed up with developer comments (example: [FlixelCommunityBot](https://github.com/FlixelCommunityBot?tab=activity)).

#### Templates ####

The script will by default use the [Markdown-formatted](http://github.github.com/github-flavored-markdown/) templates found in the [`templates`](templates/) directory. You can edit those, or point to your own templates from the config file.

#### Examples ####

![Example result of an imported pull request](https://raw.github.com/IQAndreas/github-issues-import/docs/example-imported-issue.png)

* [**Example issue (with label)**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/1) ([original](https://github.com/IQAndreas/github-issues-import/issues/1))
* [**Example pull request**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/2) ([original](https://github.com/IQAndreas/github-issues-import/issues/2))
* [**Example issue with comments**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/3) ([original](https://github.com/IQAndreas/github-issues-import/issues/3))
* [**Example issue with milestone**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/24) ([original](https://github.com/IQAndreas/github-issues-import/issues/9))


