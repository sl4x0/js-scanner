(function(W, d, s, u, l, e, t) {
 W[l] = W[l] || function() {
(W[l].q = W[l].q || []).push(arguments); 
}; W[l].q = [], e = d.createElement(s),
t = d.getElementsByTagName(s)[0]; e.async = 1; e.src = u; t.parentNode.insertBefore(e, t);
}(window, document, "script", "https://a.cdn.ua.ncsoft.com/sdk.js", "uancsoft"));
uancsoft("init", "GS-100932");
uancsoft("onload", function() {
    gtag("config", "DC-9774013");
    gtag("event", "conversion", {
    allow_custom_scripts : true,
    send_to              : "DC-9774013/gsnle0/games0+unique",
    dc_custom_params     :

    { match_id : uancsoft("get", "gsid") }
    });
});
window.dataLayer = window.dataLayer || [];
function gtag(){window.dataLayer.push(arguments);}
gtag('js', new Date());