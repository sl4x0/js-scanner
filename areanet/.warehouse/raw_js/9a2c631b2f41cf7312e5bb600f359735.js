(function() {
    "use strict";

    function setCookie(key, val, expiration) {
        document.cookie = key + "=" + val +
            ";path=/" +
            ";domain=." + location.hostname.split(".").slice(-2).join(".") +
            (!!expiration ? ";expires=" + expiration : "") +
            ";SameSite=None;Secure";
    }

    function getMatch(haystack, needle) {
        var match = haystack.match(needle);

        if (match && match.length > 1) {
            return match[1];
        }
    }

    /*
     * RFC4122-compliant UUID generator that uses date offset to prevent
     * collisions from Math.random shortcomings:
     * http://stackoverflow.com/a/8809472
     */
    function GUID() {
        var d = Date.now(),
            uuid = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
                var r = (d + Math.random() * 16) % 16 | 0;

                d = Math.floor(d / 16);

                return (c === "x" ? r : (r & 0x7 | 0x8)).toString(16);
            });

        return uuid;
    }

    var trackingRoot     = "https://www.guildwars2.com/tracking/cid/landing",
        cidParam         = /(?:\?|\&)cid=([^\&]+)/,
        cidKeyCookie     = /(?:^|;)\s*cidKey=([^;$]+)/,
        cidExpiration    = (new Date(Date.now() + 1000 * 60 * 60 * 24 * 30)).toUTCString(),
        cid              = getMatch(location.search, cidParam), // unique per link
        cidKey           = getMatch(document.cookie, cidKeyCookie), // unique per user
        trackingImg;

    if (cid) {
        setCookie("cid", cid, cidExpiration);
        setCookie("cidKey", cidKey || GUID(), cidExpiration); // refresh exp

        trackingImg = document.createElement("img");
        trackingImg.style.display = "none";

        // doesn't include cid or cidKey, but gets sent as cookie with img req
        trackingImg.src = trackingRoot +
            "?path=" + encodeURIComponent(location.pathname + location.search) +
            "&site=" + encodeURIComponent(location.host) +
            "&referrer=" + encodeURIComponent(document.referrer);

        document.body.appendChild(trackingImg);
    }
}());
