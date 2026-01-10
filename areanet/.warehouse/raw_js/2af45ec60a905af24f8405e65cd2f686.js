YUI.add("image-compare",function(c){(e=document.createElement("script")).defer=!0,e.src="https://cdn.jsdelivr.net/npm/img-comparison-slider@8/dist/index.js",document.head.appendChild(e),(e=document.createElement("link")).rel="stylesheet",e.href="https://cdn.jsdelivr.net/npm/img-comparison-slider@8/dist/styles.css",document.head.appendChild(e);var e=c.all("[data-yui='image-compare-fullscreen']");e.isEmpty()||e.each(r=>{r.on("click",e=>{var t=r.getAttribute("data-left"),i=r.getAttribute("data-right");let a=c.Node.create(`<div class="image-compare-lb-scrim">
                    <div class="image-compare-lb-content">
                        <button class="image-compare-lb-close" aria-label="Close dialog"></button>

                        <img-comparison-slider>
                            <img slot="first" src="${t}" />
                            <img slot="second" src="${i}" />
                        </img-comparison-slider>
                    </div>
                </div>`);c.one("body").append(a),a.one(".image-compare-lb-close").on("click",()=>{a.remove(!0)}),a.on("click",e=>{e.target._yuid===e.currentTarget._yuid&&a.remove(!0)}),window.document.addEventListener("keydown",e=>{"Escape"===e.key&&a.remove(!0)},{once:!0}),e.preventDefault()})})},"@VERSION",{requires:["node","event","dom-base"]});