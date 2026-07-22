---
title: Recently
---
<!-- Photos are picked up automatically from the photos/ folder, newest first.
     Just drop iPhone portrait photos in there and rebuild.
     Suggested size: 1200 × 1600 px (3:4) or any portrait crop. -->
<div class="photo-grid">
{% assign photos = site.static_files | where_exp: "file", "file.path contains '/photos/'" %}
{% assign photos = photos | where_exp: "file", "file.extname != '.svg'" %}
{% assign photos = photos | sort: "modified_time" | reverse %}
{% for photo in photos %}
  {% assign photo_alt = photo.name | remove: photo.extname | replace: '-', ' ' | replace: '_', ' ' | capitalize %}
  <figure>
    <img src="{{ photo.path | relative_url }}" alt="{{ photo_alt }}" loading="lazy">
  </figure>
{% endfor %}
</div>
