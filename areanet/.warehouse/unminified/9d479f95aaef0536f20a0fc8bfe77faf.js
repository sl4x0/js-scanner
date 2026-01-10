YUI.add("shop-item", function(t) {
  new t.Lightbox({
    items: ".photo-list .item-photo",
    render: !0
  })
}, "@VERSION@", {
  requires: ["lightbox-widget"]
});