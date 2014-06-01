---
layout: slate
permalink: configuration/index.html
title: Configuration options
subtitle: Configuration options
---

By default, the script will look in the same directory as the script for a file named `config.ini`. Alternatively, you can store the config file in a different location and use the `--config <filename>` option to specify where the file is located. Adding the `.ini` extension to configuration files is recommended for clarity, but not necessary.

If you want the script to _completely ignore_ the default config file and only use command line arguments, pass the `--no-config` flag when running the script. This is useful for if you usually have "default" authentication options in `config.ini`, but want to temporarily ignore them and run the script as a different user.

The following is a minimal version of a configuration file; in all these examples, the sections (e.g. `[login]` and `[format]`) **are required** before listing the configuration options inside of them:

```
# Lines starting with the # character are ignored and treated as comments

[login]
username = OctoDog
password = plaintext_pa$$w0rd

[source]
repository = OctoCat/Hello-World

[target]
repository = OctoDog/Hello-World
```

**Warning:** The password is stored in plain-text, so avoid storing the config file in a public repository. To avoid this, you can instead pass the username and/or password as arguments by using the `-u <username>` and `-p <password>` flags respectively. If the username or password is not passed in from either of these locations, the user will be prompted for them when the script runs.

The `username` can also be the email address associated with the GitHub account:

```
username = admin@octodog.org
```

### <a id="enterprise"></a> Enterprise Accounts and Advanced Login Options

If you are using [GitHub for Enterprise](https://enterprise.github.com/), thanks to the help of [Joshua Rountree](https://github.com/joshuairl), there is support for that. These changes also allow you to specify a different username and password for the source and target repositories, even if both of them are hosted on GitHub.

The command line options `--username` and `--password` do not allow you to specify which repository the credentials apply to, so unless you use the same credentials for both servers, a config file _must_ be used.

```
[source]
server = github.com
repository = OctoCat/Hello-World
username = octocat@github.com
password = plaintext_pa$$w0rd

[target]
server = octodog.org
repository = OctoDog/Hello-World
username = admin@octodog.org
password = plaintext_pass\/\/ord
```

### <a id="formatting-dates"></a> Formatting Dates

You can specify how the date is displayed when issues are created in the destination repository. Note that when the issues are imported as comments in the target repository, there is no way to dynamically update the time based on the logged in user's timezone. Instead, all dates and times are in [Greenwich Mean Time (GMT)](http://wwp.greenwichmeantime.com/).

This is the default format used by the script; for a full list of possible options, see [the Python docs](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior): 

```
[format]
date = %A %b %d, %Y at %H:%M GMT
```

Which results in the following date and time:

```
Thursday Sep 12, 2013 at 22:42 GMT
```

If you are unsure of what format to use, just setting the date format to `%c` will automatically retrieve the default date and time format used in your region (useful if everyone working on the target repository are from the same locale).


### <a id="custom-templates"></a> Custom templates

In the `[format]` section you can also define the location of any templates (and by default will use the templates found in this project's `templates` directory). Unless an absolute path is given, the templates are relative to the current working directory.

```
[format]
issue_template =        templates/issue.md
pull_request_template = templates/pull_request.md
comment_template =      templates/comment.md
```

See [_Custom Templates_]({{ site.url }}/templates) for more details if you would like to create your own templates. 


