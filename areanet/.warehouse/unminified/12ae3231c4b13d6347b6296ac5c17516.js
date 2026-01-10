YUI.add("faq", function(a) {
  var l = a.one("#faq-glossary");
  a.all("#faq-glossary div").hide(), a.all("#faq-glossary div").toggleView(), l.delegate("click", function(a) {
    a.preventDefault(), this.next().toggleView()
  }, ".faq-glossary li > a")
});