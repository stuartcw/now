---
title: What is this page and how did I make it
---
This is a "now page": a single page saying what I'm focused on at this point in
my life. The idea comes from Derek Sivers, and the convention is explained at
[nownownow.com/about](https://nownownow.com/about). It sits somewhere between a
bio, which says who you are, and a blog, which says what you were thinking on a
particular day. A now page says what has my attention at the moment, and it gets
rewritten whenever that changes.

The source is a [Jekyll](https://jekyllrb.com) site in the GitHub repo
[stuartcw/now](https://github.com/stuartcw/now). Each part of this page is a
separate Markdown file in `_sections/`, and the page you're reading is those
files sorted by filename and concatenated. Editing the page means editing one
small file, which is the point: the easier it is to update, the more likely it
stays true.

Publishing is handled by Cloudflare. Pushing to `main` triggers a Workers build
that runs `bundle exec jekyll build` to generate the static HTML, then deploys it
with `wrangler`. The site is served as static assets by a Worker, with no server
to run or maintain.

Getting it to live at `/now` rather than on its own subdomain takes two pieces
that have to agree. A Worker *route* claims the paths `stuartwoodward.com/now`
and `/now/*`, so requests for those are handed to this Worker while the rest of
the domain carries on as before. Then, because the Worker matches incoming URL
paths against the files it's serving, the build output is nested into a `now/`
directory and Jekyll's `baseurl` is set to `/now` so that every link and image
points at the right place. Miss either half and you get a page that builds
perfectly and serves nothing.
