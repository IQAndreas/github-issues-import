---
layout: slate
permalink: index.html
---
### What is this place?

Don't you just hate it when you have several [GitHub pages](http://pages.github.com/) for your projects that are all supposed to share the same layout, then you go and tweak the layout a bit, forcing you to update the changes and rebuild every single project page?

Since you cannot inherit [Jekyll](http://jekyllrb.com/) projects from another project, this at least helps soften the blow.

The CSS, JavaScript, and images are all stored here (and accessed via absolute URLs [[1]](https://github.com/IQAndreas/gh-pages-template/blob/gh-pages/_includes/imports/stylesheets.html) [[2]](http://static.iqandreas.com/assets/stylesheets/slate/main.css)), so if you update them once, the changes will propagate to all pages that use them. The changes to `_layouts`, `_includes`, and `_plugins` are only a `git merge` away from being updated in (but this is still very manual, and annoying, and needs to be done for every single project you want the change applied to).

### This isn't the best solution

GitHub staff (and/or Jekyll authors), if you are reading this, please let us allow Jekyll projects/GitHub Pages to inherit from other other projects, so if the "parent" updates, all children that are affected rebuild. _Alas, I imagine this may be taxing on the GitHub Pages build servers, but at least I can dream this feature will one day be added._

### Credits

This project is generously hosted by [GitHub Pages](http://pages.github.com/), and powered by [Jekyll](http://jekyllrb.com/).

The site design is a modified version of Slate by [Jason Costello](http://twitter.com/jsncostello).

Unless otherwise indicated, everything else on this site (including images, code, and content) is owned by [Andreas Renberg](mailto:contact@iqandreas.com) and made available under [{{ site.github_license }}]({{site.github_license_url}}).

