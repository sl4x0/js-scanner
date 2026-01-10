YUI.add("media-loader", function(i) {
  var t = i.one("#loadMedia a"),
    n = i.one(t.getAttribute("href")),
    s = n.getData("atchIdx"),
    o = window.attachmentsData,
    h = window.attachmentsBase,
    r = `<li class='${n.hasClass("concept-art")?"concept":"screenshot"} media-item frame yui3-u' style='opacity: 0;'><a href='{mediaBase}{image}' target='_blank'><img src='{mediaBase}{thumb}' alt='' width='{width}' height='{height}'></a></li>`;
  t.on("click", function(e) {
    e.preventDefault();
    for (let a = 0; a < s && 0 < o.length; a++) {
      let e = o.shift(),
        t;
      "object" == typeof e ? e = t = e.img : t = e.replace(/\.jpg$/, "-139x79-crop.jpg"), n.appendChild(i.DOM.create(i.Lang.sub(r, {
        width: 139,
        height: 79,
        mediaBase: h,
        image: e,
        thumb: t
      }))).transition({
        opacity: 1,
        duration: .5,
        delay: .02 * a
      })
    }
    o.length < 1 && t.remove(), n.hasClass("screenshots") && i.fire("screenshotLightbox:init"), n.hasClass("concept-art") && i.fire("conceptartLightbox:init")
  })
}, "@VERSION@", {
  require: ["node", "event", "transition"]
});