
### GitHub Issues Import ###

This Python script allows you to import issues and pull requests from one repository to another (works even if the two repositories are not related to each other).

Fork of one of the tools by [Max Korenkov](https://github.com/mkorenkov) separated from its original location at [`mokorenkov/tools`](https://github.com/mkorenkov/tools).

#### Usage ####

Rename `config.ini.sample` to `config.ini`, and edit the fields to match your login info and repository info. **Warning:** The password is stored in plaintext, so avoid storing the config file in a public repository.
 
Run the script with the following command to import all issues into the repository defined in the config:

```
 $ python3 gh-issues-import.py
```

Or to only import some issues, run the script and include the issue numbers of all issues you wish to import (can be done for one or several issues):

```
 $ python3 gh-issues-import.py 25 26 29
```

#### Result ####

Every issue imported will create a new issue in the target repository. Remember that the ID of the issue in the new repository will most likely not be the same as the ID of the original issue. Keep this in mind when writing commit messages such as _"Closes #25"_.

If the issue is a pull request, this will be indicated on the issue, and a link to the code will be provided. However, it will be treated as a new issue in the target repository, and **not** a pull request. Pulling in the suggested code into the repository will need to be done manually.

Any comments on the issue will be imported, however, the author of all imported comments will be the account specified in the config. Instead, a link and header is provided for each comment indicating who the original author was and the original date and time of the comment. Any subsequent comments added to the issue after it has been imported into the target repository will not be included.

If allowed by GitHub's policies, it may be a good idea to use a "neutral" account to import the issues and issue comments to avoid imported comments from getting mixed up with developer comments (example: [FlixelCommunityBot](https://github.com/FlixelCommunityBot?tab=activity)).

Labels attached to the issue will be imported and added to the target repo if they do not already exist there.

Any milestones attached to issues will simply be ignored and need to be added manually. This is because they have different issue IDs across repos (like imported issues do) which will cause problems in the target repo. Importing Milestones has been temporarily disabled until this has been fixed.

#### Examples ####

![Example result of an imported pull request](https://raw.github.com/IQAndreas/github-issues-import/docs/example-imported-issue.png)

* [**Example issue (with label)**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/1) ([original](https://github.com/IQAndreas/github-issues-import/issues/1))
* [**Example pull request**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/2) ([original](https://github.com/IQAndreas/github-issues-import/issues/2))
* [**Example issue with comments**](https://github.com/IQAndreas-testprojects/github-issues-import-example/issues/3) ([original](https://github.com/IQAndreas/github-issues-import/issues/3))


