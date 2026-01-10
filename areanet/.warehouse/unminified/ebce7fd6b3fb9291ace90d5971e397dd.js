YUI.add("media", function(n) {
  var o, e, t, r, s = n.one(".video-selector");

  function c(e) {
    return new n.Lightbox({
      items: e,
      render: !0
    })
  }
  s && (o = s.one(".featured iframe"), s.delegate("click", function(e) {
    var t = e.currentTarget.getData("vidid");
    t && (e.preventDefault(), o.set("src", n.Lang.sub("//www.youtube.com/embed/{vidId}?rel=0&modestbranding=1&showinfo=0", {
      vidId: t
    })))
  }, ".inl-video")), e = c(".screenshots .screenshot"), t = c(".lb-screenshots .screenshot"), r = c(".concept-art .concept"), n.on({
    "screenshotLightbox:init": function() {
      e.destroy(), t.destroy(), e = c(".screenshots .screenshot"), t = c(".lb-screenshots .screenshot")
    },
    "conceptartLightbox:init": function() {
      r.destroy(), r = c(".concept-art .concept")
    }
  })
}, "@VERSION@", {
  requires: ["lightbox-widget"]
});