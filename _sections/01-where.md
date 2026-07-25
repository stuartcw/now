---
title: Where I am
---
<!-- Location comes from _includes/location.txt, maintained separately from
     this file. If it's a Google Maps "Embed a map" URL (Share > Embed a map
     in Google Maps, contains "/maps/embed"), a map is shown. Anything else
     is shown as plain text. -->
{% capture location %}{% include location.txt %}{% endcapture %}
{% assign location = location | strip %}
{% if location contains '/maps/embed' %}
<div class="map-embed">
  <iframe src="{{ location }}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
</div>
{% else %}
{{ location }}
{% endif %}
