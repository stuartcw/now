# now

The source for [stuartwoodward.com/now](https://stuartwoodward.com/now/).

## What is this page

This is a "now page": a single page saying what I'm focused on at this point in
my life. The idea comes from Derek Sivers, and the convention is explained at
[nownownow.com/about](https://nownownow.com/about). It sits somewhere between a
bio, which says who you are, and a blog, which says what you were thinking on a
particular day. A now page says what has my attention at the moment, and it gets
rewritten whenever that changes.

## How it's built

A [Jekyll](https://jekyllrb.com) static site with no plugins or JavaScript.

Each part of the page is a separate Markdown file in `_sections/`, exposed as a
Jekyll collection with `output: false`. `index.md` sorts them by path and
concatenates them, so filenames control the running order:

```
_sections/
  01-where.md
  02-working-on.md
  03-learning.md
  04-reading.md
  05-recently.md
  06-about-this-page.md
```

Each file carries a `title` in its front matter and its body below. To add a
section, drop in a new numbered file. To reorder, renumber.

Photos for the "Recently" section are picked up automatically from `photos/`.
Drop an image file in and rebuild — `_sections/05-recently.md` loops over
`site.static_files`, sorted newest-first by modification time, and renders one
`<figure>` per photo with an alt attribute derived from the filename. There
are no captions and nothing to hand-edit; SVGs in that folder are skipped, so
it can also hold non-photo assets if needed.

## Running it locally

```
bundle install
bundle exec jekyll serve
```

Then open <http://localhost:4000/now/> — note the `/now/` suffix, which `baseurl`
requires. `Gemfile.lock` is committed, so local and CI resolve to the same gem
versions.

Enable the repo's git hooks once per clone:

```
git config core.hooksPath .githooks
```

This runs `.githooks/pre-commit`, which strips EXIF/GPS metadata from any
staged photo before the commit is created — needed since `photos/` is served
publicly and iPhone photos carry GPS coordinates by default. It requires
`exiftool` or ImageMagick (`magick`/`convert`) on `PATH`; the commit is
blocked with an install hint if neither is found.

## How it's published

Pushing to `main` triggers a Cloudflare Workers build against this repo:

| Setting        | Value                              |
| -------------- | ---------------------------------- |
| Build command  | `bundle exec jekyll build -d _site/now` |
| Deploy command | `npx wrangler deploy`              |
| Root directory | `/`                                |

The generated HTML is then served as static assets by a Worker. There's no
server to run.

## How `/now` is mapped onto the domain

The page lives at a *path* on an existing domain rather than on a subdomain,
which takes two pieces that have to agree with each other.

**A route claims the path.** `wrangler.jsonc` declares:

```jsonc
"routes": [
  { "pattern": "stuartwoodward.com/now",   "zone_name": "stuartwoodward.com" },
  { "pattern": "stuartwoodward.com/now/*", "zone_name": "stuartwoodward.com" }
]
```

Requests for those paths are handed to this Worker; the rest of the domain
carries on unaffected. This works because the `stuartwoodward.com` DNS records
are proxied through Cloudflare — routes only fire on traffic through the edge.
The two patterns are kept separate deliberately: a single `/now*` would also
match `/nowhere`.

**The output is nested to match.** The Worker maps incoming URL paths onto the
files it serves, so a request for `/now/` looks for `now/index.html` in the
assets directory. Two settings make that true:

- `-d _site/now` on the build command, so Jekyll writes into a `now/`
  subdirectory of the assets root.
- `baseurl: "/now"` in `_config.yml`, so `relative_url` prefixes every link and
  image.

Miss either half and the build goes green while the page 404s. `baseurl` alone
only rewrites links; it does not nest the output.

Note that adding `routes` to `wrangler.jsonc` disables the `workers.dev`
subdomain by default. That's intentional here — the site is reachable at its real
URL, and a second URL serving identical content invites duplicate-content
indexing. Setting `"workers_dev": true` would bring it back, though only at
`/now/`, never at the root.

## Gotchas

- **`npx bundle` doesn't work.** `bundle` is a Ruby gem, not an npm package. If
  the build command is left unset, `wrangler deploy` auto-detects the project,
  guesses a build command of `npx bundle exec jekyll build`, and fails with
  `could not determine executable to run`. Committing `wrangler.jsonc` stops the
  auto-detection; setting the build command explicitly gives it the right one.
- **`wrangler.jsonc` is in `exclude`** in `_config.yml`, otherwise Jekyll copies
  it into the build output and it gets served publicly.
