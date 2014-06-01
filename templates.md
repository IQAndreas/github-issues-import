---
layout: slate
permalink: templates/index.html
title: Custom Templates
subtitle: Custom Templates
---

The script will by default use the [Markdown-formatted](http://github.github.com/github-flavored-markdown/) templates found in the [`templates`]({{site.github_url}}/tree/master/templates/) directory for importing issues, pull requests, and comments. These are written in US English, and contain some fancy formatting including links to the GitHub profile and Gravatar images for the person who originally authored the issue or comment.

Here you can see examples of how those default templates render:

{% include example-imported-issues.md %}

### <a id="creating-custom-templates"></a> Creating Custom Templates

If you would like, you can make changes to the existing templates, or create your own from scratch. Issues and comments posted to GitHub [support Markdown](https://help.github.com/articles/github-flavored-markdown) and some HTML.

The following illustrates a very simple template for comments (you look at the default templates included with the library for more advanced examples):

```
**Comment by [${user_name}](${user_url})** _${date}_

----

${body}
```

As you can see, a small set of "variables" can be used within your template, and can be retrieved like this: `${user_name}`. The following variables are available:

 * `user_name` - Name of the author of the issue, pull request, or comment
 * `user_url` - URL to the author's GitHub profile
 * `user_avatar` - URL to an avatar image defined for the user (uses Gravatar, at least on GitHub's servers)
 * `date` - The date the issue, pull request, or comment was written. Will be formatted according to the format specified in the configs; see [_Configuration Options: Formatting Dates_]({{site.url}}/configuration/#formatting-dates).
 * `url` - URL to the issue, pull request, or comment
 * `body` - The main content written by the author
 
If you want other data, such as the URL to the code included with the pull request, some "manual" work is required: `${url}/commits`.

### <a id="using-custom-templates"></a> Using the Custom Templates

If you created _new_ templates instead of editing the existing ones, you have to tell the script where these templates can be found; you can do this in two ways:

 1. In the configuration file - See [_Configuration Options: Custom Templates_]({{site.url}}/configuration/#custom-templates)
 2. As an argument - See [_Command Line Arguments: Custom Templates_]({{site.url}}/arguments/#custom-templates)


### <a id="contributing"></a> Contributing

If you have created a template that may benefit others, such as a translation into a different language or improved formatting, please share this change by [opening an issue on GitHub]({{ site.github_url }}/issues), or by [contacting me](mailto:contact@iqandreas.com).

