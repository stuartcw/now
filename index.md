---
layout: default
title: Now
description: What I'm doing now
updated: 2026-07-01
---

{% assign sections = site.sections | sort: 'path' %}
{% for section in sections %}
<div class="now-section">
  <h2>{{ section.title }}</h2>
  {{ section.content }}
</div>
{% endfor %}
