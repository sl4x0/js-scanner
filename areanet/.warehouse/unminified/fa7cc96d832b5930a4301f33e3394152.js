var tp_config = {
  groups: {
    'Public/app/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/app/',
      base: '/app/',
      modules: {
        'app-ntp': {
          path: 'app-ntp.2c27d060.js',
          requires: ['app-state', 'unauthorized', 'gw2-enums', 'sell', 'browse', 'transactions', 'home', 'view-order', 'component-balance', 'component-filters', 'component-delivery-box', 'component-tabs', 'component-categories', 'component-item-table', 'component-breadcrumbs', 'css-app', 'css-grid', 'button', 'util-text-keys', 'util-optional', 'util-items', 'util-log']
        },
        'app-state': {
          path: 'app-state.cc7301aa.js',
          requires: ['gw2-enums', 'filter-types', 'util-log']
        }
      }
    },
    'Public/components/balance/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/balance/',
      base: '/components/balance/',
      modules: {
        'component-balance': {
          path: 'component-balance.cacc6fff.js',
          requires: ['css-balance', 'element-coins', 'number-floater-plugin']
        }
      }
    },
    'Public/components/breadcrumbs/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/breadcrumbs/',
      base: '/components/breadcrumbs/',
      modules: {
        'component-breadcrumbs': {
          path: 'component-breadcrumbs.bbcb7ed4.js',
          requires: ['css-breadcrumbs', 'util-optional']
        }
      }
    },
    'Public/components/categories/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/categories/',
      base: '/components/categories/',
      modules: {
        'component-categories': {
          path: 'component-categories.6ce4b00b.js',
          requires: ['css-categories', 'navigation', 'element-item', 'util-optional', 'util-log', 'node-event-simulate']
        }
      }
    },
    'Public/components/delivery-box/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/delivery-box/',
      base: '/components/delivery-box/',
      modules: {
        'component-delivery-box': {
          path: 'component-delivery-box.e3f34a.js',
          requires: ['css-delivery', 'util-optional', 'element-item', 'element-coins', 'number-floater-plugin']
        }
      }
    },
    'Public/components/env/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/env/',
      base: '/components/env/',
      modules: {
        'component-env': {
          path: 'component-env.1a794b16.js',
          requires: ['css-env']
        }
      }
    },
    'Public/components/filters/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/filters/',
      base: '/components/filters/',
      modules: {
        'component-filters': {
          path: 'component-filters.58049cae.js',
          requires: ['event-outside', 'gw2-enums', 'filter-types', 'util-optional', 'css-filters']
        }
      }
    },
    'Public/components/item-table/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/item-table/',
      base: '/components/item-table/',
      modules: {
        'component-item-table': {
          path: 'component-item-table.edff5ca0.js',
          requires: ['item-table-controller', 'item-table-view']
        },
        'item-table-cells': {
          path: 'item-table-cells.55687b8d.js',
          requires: ['util-relative-time', 'util-items', 'element-coins', 'element-item']
        },
        'item-table-controller': {
          path: 'item-table-controller.db089b01.js',
          requires: ['sts-request']
        },
        'item-table-data': {
          path: 'item-table-data.4884173c.js'
        },
        'item-table-outer': {
          path: 'item-table-outer.4ba8b78b.js',
          requires: ['util-optional', 'item-table-data']
        },
        'item-table-view': {
          path: 'item-table-view.d6e8c520.js',
          requires: ['util-optional', 'util-text-keys', 'item-table-data', 'item-table-cells', 'item-table-viewport', 'item-table-outer', 'css-item-table', 'css-spinner']
        },
        'item-table-viewport': {
          path: 'item-table-viewport.642b9a7.js'
        },
        'util-relative-time': {
          path: 'util-relative-time.55ebd835.js',
          requires: .base
        }
      }
    },
    'Public/components/tabs/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/components/tabs/',
      base: '/components/tabs/',
      modules: {
        'component-tabs': {
          path: 'component-tabs.91583818.js',
          requires: ['css-tabs']
        }
      }
    },
    'Public/gen/gw2/shared/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/shared/',
      base: '/gen/gw2/shared/',
      modules: {
        'micro-gw2-maintenance': {
          path: 'micro-gw2-maintenance.gen.f2608e44.js',
          requires: .template
        },
        'micro-gw2-unauthorized': {
          path: 'micro-gw2-unauthorized.gen.a9979162.js',
          requires: .template
        },
        'css-gw2': {
          path: 'gw2.24e2ab79.css',
          type: 'css'
        },
        'css-maintenance': {
          path: 'maintenance.e0265fc.css',
          type: 'css'
        },
        'css-unauthorized': {
          path: 'unauthorized.a4c12be1.css',
          type: 'css'
        }
      }
    },
    'Public/gw2/elements/coins-mithril/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/elements/coins-mithril/',
      base: '/gw2/elements/coins-mithril/',
      modules: {
        'element-coins': {
          path: 'coins.e1389aaa.js',
          requires: ['util-optional', 'css-coins']
        }
      }
    },
    'Public/gw2/elements/item-mithril/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/elements/item-mithril/',
      base: '/gw2/elements/item-mithril/',
      modules: {
        'element-item': {
          path: 'item.eff1b870.js',
          requires: ['gw2-enums', 'util-optional', 'util-text-keys', 'css-item']
        }
      }
    },
    'Public/gw2/native/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/native/',
      base: '/gw2/native/',
      modules: {
        'native-api-ime': {
          path: 'native-api-ime.677234ea.js',
          requires: ['native-stats']
        },
        'native-call': {
          path: 'native-call.d9953d70.js',
          requires: .promise
        },
        'native-scale': {
          path: 'native-scale.8989021c.js',
          condition: {
            test: function() {
              'use strict';
              return window.self === window.top
            }
          }
        },
        'native-stats': {
          path: 'native-stats.302e17af.js',
          requires: ['event-custom-base']
        }
      }
    },
    'Public/gw2/prompt/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/prompt/',
      base: '/gw2/prompt/',
      modules: {
        prompt: {
          path: 'prompt.7f1c9b51.js',
          requires: ['css-prompt']
        }
      }
    },
    'Public/gw2/shared/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/shared/',
      base: '/gw2/shared/',
      modules: {
        'account-status': {
          path: 'account-status.39e0680c.js',
          requires: ['event', 'sts-request']
        },
        'gw2-enums': {
          path: 'gw2-enums.5ab99e92.js'
        },
        'number-floater-plugin': {
          path: 'number-floater-plugin.9ee15c62.js',
          requires: ['plugin', 'base', 'node', 'transition']
        },
        'old-build': {
          path: 'old-build.4b474433.js',
          requires: ['node', 'micro-gw2-maintenance', 'css-maintenance'],
          condition: {
            trigger: 'unauthorized',
            when: 'before',
            test: function(e) {
              'use strict';
              return GW2.config.options.buildId > 0
            }
          }
        },
        unauthorized: {
          path: 'unauthorized.f10ab380.js',
          requires: ['sts-userinfo', 'sts-request', 'css-unauthorized', 'micro-gw2-unauthorized']
        }
      }
    },
    'Public/gw2/sts/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/sts/',
      base: '/gw2/sts/',
      modules: {
        'sts-http': {
          path: 'sts-http.7f6c008f.js',
          requires: ['io-base', 'promise']
        },
        'sts-request-jssrv': {
          path: 'sts-request-jssrv.f1e93203.js',
          requires: ['promise', 'sts-http', 'native-stats'],
          condition: {
            trigger: 'sts-request',
            when: 'after',
            test: function(e) {
              'use strict';
              return !window.native || window.native.stubbed || !GW2.config.features.cliGate
            }
          }
        },
        'sts-request-native': {
          path: 'sts-request-native.4b2ecf5c.js',
          requires: .promise,
          condition: {
            trigger: 'sts-request',
            when: 'after',
            test: function() {
              'use strict';
              return window.native && !window.native.stubbed && GW2.config.features.cliGate
            }
          }
        },
        'sts-request': {
          path: 'sts-request.eb464748.js',
          requires: .promise
        },
        'sts-userinfo': {
          path: 'sts-userinfo.9f4602b6.js',
          requires: ['sts-request']
        }
      }
    },
    'Public/gw2/util/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/util/',
      base: '/gw2/util/',
      modules: {
        'util-coins': {
          path: 'util-coins.f279a29c.js',
          requires: ['node-base']
        },
        'util-log': {
          path: 'util-log.15c1a463.js'
        },
        'util-optional': {
          path: 'util-optional.27796170.js'
        },
        'util-restricted': {
          path: 'util-restricted.2d47fa20.js'
        },
        'util-text-keys': {
          path: 'util-text-keys.8a710828.js'
        }
      }
    },
    'Public/sections/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/sections/',
      base: '/sections/',
      modules: {
        browse: {
          path: 'browse.18233913.js',
          requires: ['app-state', 'gw2-enums', 'filter-types', 'navigation', 'util-items']
        },
        sell: {
          path: 'sell.b14e981d.js',
          requires: ['sts-request', 'gw2-enums', 'util-items', 'navigation']
        },
        transactions: {
          path: 'transactions.7b777ee8.js',
          requires: ['app-state', 'navigation', 'sts-request', 'util-items']
        }
      }
    },
    'Public/sections/home/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/sections/home/',
      base: '/sections/home/',
      modules: {
        home: {
          path: 'home.53b8497c.js',
          requires: ['util-items', 'util-optional', 'transactions', 'element-item', 'css-home']
        }
      }
    },
    'Public/sections/order/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/sections/order/',
      base: '/sections/order/',
      modules: {
        'extension-last-viewed': {
          path: 'extension-last-viewed.b59bf35.js',
          requires: ['array-extras', 'promise', 'util-text-keys']
        },
        'model-coins': {
          path: 'model-coins.2c568e10.js',
          requires: ['base-build', 'model']
        },
        'model-listings': {
          path: 'model-listings.c96e3015.js',
          requires: ['base-build', 'model', 'sts-request']
        },
        'model-orderstate': {
          path: 'model-orderstate.f10d9f0a.js',
          requires: ['base-build', 'model', 'gw2-enums', 'sts-request', 'util-coins', 'element-coins', 'account-status', 'model-coins', 'model-listings', 'extension-last-viewed', 'util-items', 'util-log']
        },
        'view-order': {
          path: 'view-order.c38f8d43.js',
          requires: ['base-build', 'view', 'node', 'prompt', 'sts-request', 'util-coins', 'util-optional', 'util-restricted', 'model-orderstate', 'element-item', 'element-coins', 'css-order', 'css-spinner']
        }
      }
    },
    'Public/shared/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/shared/',
      base: '/shared/',
      modules: {
        'filter-types': {
          path: 'filter-types.4844948.js',
          requires: ['gw2-enums']
        },
        navigation: {
          path: 'navigation.d583393b.js'
        },
        'util-items': {
          path: 'util-items.6a7b0d8b.js',
          requires: ['sts-request', 'util-text-keys', 'account-status']
        }
      }
    },
    'Public/gen/app/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/app/',
      base: '/gen/app/',
      modules: {
        'css-app': {
          path: 'app.3ff5b25d.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/balance/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/balance/',
      base: '/gen/components/balance/',
      modules: {
        'css-balance': {
          path: 'balance.c8b01275.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/breadcrumbs/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/breadcrumbs/',
      base: '/gen/components/breadcrumbs/',
      modules: {
        'css-breadcrumbs': {
          path: 'breadcrumbs.7a9fdb0f.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/categories/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/categories/',
      base: '/gen/components/categories/',
      modules: {
        'css-categories': {
          path: 'categories.c5905087.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/delivery-box/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/delivery-box/',
      base: '/gen/components/delivery-box/',
      modules: {
        'css-delivery': {
          path: 'delivery.c5a8e639.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/env/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/env/',
      base: '/gen/components/env/',
      modules: {
        'css-env': {
          path: 'env.a9d4c5d0.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/filters/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/filters/',
      base: '/gen/components/filters/',
      modules: {
        'css-filters': {
          path: 'filters.a6979a2d.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/item-table/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/item-table/',
      base: '/gen/components/item-table/',
      modules: {
        'css-item-table': {
          path: 'item-table.c20fad03.css',
          type: 'css'
        }
      }
    },
    'Public/gen/components/tabs/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/components/tabs/',
      base: '/gen/components/tabs/',
      modules: {
        'css-tabs': {
          path: 'tabs.c7c50114.css',
          type: 'css'
        }
      }
    },
    'Public/gen/gw2/button/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/button/',
      base: '/gen/gw2/button/',
      modules: {
        'css-button': {
          path: 'button.2fcb419c.css',
          type: 'css'
        }
      }
    },
    'Public/gen/gw2/elements/coins-mithril/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/elements/coins-mithril/',
      base: '/gen/gw2/elements/coins-mithril/',
      modules: {
        'css-coins': {
          path: 'coins.c22a6693.css',
          type: 'css'
        }
      }
    },
    'Public/gen/gw2/elements/item-mithril/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/elements/item-mithril/',
      base: '/gen/gw2/elements/item-mithril/',
      modules: {
        'css-item': {
          path: 'item.10032b61.css',
          type: 'css'
        }
      }
    },
    'Public/gen/gw2/prompt/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/prompt/',
      base: '/gen/gw2/prompt/',
      modules: {
        'css-prompt': {
          path: 'prompt.4421bc.css',
          type: 'css'
        }
      }
    },
    'Public/gen/gw2/scroller/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/scroller/',
      base: '/gen/gw2/scroller/',
      modules: {
        'css-scroller': {
          path: 'scroller.cb3f66d1.css',
          type: 'css'
        }
      }
    },
    'Public/gen/gw2/spinner/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/gw2/spinner/',
      base: '/gen/gw2/spinner/',
      modules: {
        'css-spinner': {
          path: 'spinner.c9efa2ea.css',
          type: 'css'
        }
      }
    },
    'Public/gen/sections/home/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/sections/home/',
      base: '/gen/sections/home/',
      modules: {
        'css-home': {
          path: 'home.1c14f23f.css',
          type: 'css'
        }
      }
    },
    'Public/gen/sections/order/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/sections/order/',
      base: '/gen/sections/order/',
      modules: {
        'css-order': {
          path: 'order.b76cc452.css',
          type: 'css'
        }
      }
    },
    'Public/gen/shared/less/': {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gen/shared/less/',
      base: '/gen/shared/less/',
      modules: {
        'css-grid': {
          path: 'grid.540ab286.css',
          type: 'css'
        }
      }
    },
    ejsBase: {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/services/combo/js/',
      base: '/services/combo/js/',
      modules: {
        'ejs-base': {
          path: 'ejs-base.js',
          requires: ['yui-base', 'escape']
        }
      }
    },
    'template://': {
      combine: !0,
      root: '',
      base: '/combo/_',
      patterns: {
        'template://': {
          configFn: function(e) {
            'use strict';
            var t = e.name.replace(e.group, '/').replace('.ejs', '');
            e.path = t + (tp_config.hash ? '/' + tp_config.hash : '') + '.ejs', e.requires = ['ejs-base']
          }
        }
      }
    },
    'i18n://': {
      combine: !0,
      root: '',
      base: '/combo/_',
      patterns: {
        'i18n://': {
          configFn: function(e) {
            'use strict';
            var t = tp_config.pageLang,
              s = e.name.replace(e.group, '/');
            t || (t = tp_config.pageLang = document.documentElement.lang), e.path = '/' + t + s + (tp_config.hash ? '/' + tp_config.hash : '') + '.i18n'
          }
        }
      }
    },
    raw: {
      combine: !0,
      comboBase: 'https://2tradingpost.staticwars.com/combo/_',
      root: '/gw2/',
      base: '/gw2/',
      modules: {
        button: {
          path: 'button/button.8e1699bd.js',
          requires: ['css-button']
        },
        throttle: {
          path: 'scroller/throttle.86606381.js'
        },
        scroller: {
          path: 'scroller/scroller.14a54742.js',
          requires: ['throttle', 'css-scroller']
        }
      }
    }
  }
};
GW2.configs.push(tp_config)
GW2.start("css-gw2", "app-ntp");