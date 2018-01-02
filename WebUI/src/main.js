// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import VeeValidate from 'vee-validate'
import App from './App'
import store from './store'
import router from './router'
import { sync } from 'vuex-router-sync'
import VuesticPlugin from 'src/components/vuestic-components/vuestic-components-plugin'
import axios from 'axios'
import VueAxios from 'vue-axios'
import Snotify from 'vue-snotify'
// You also need to import the styles. If you're using webpack's css-loader, you can do so here:
import 'vue-snotify/styles/material.css' // or dark.css or simple.css
var VueCookie = require('vue-cookie')


Vue.use(VueCookie)
Vue.use(Snotify)
Vue.use(VueAxios, axios)
Vue.use(VuesticPlugin)
Vue.use(BootstrapVue)

// NOTE: workaround for VeeValidate + vuetable-2
Vue.use(VeeValidate, {fieldsBagName: 'formFields'})

sync(store, router)

let mediaHandler = () => {
  if (window.matchMedia(store.getters.config.windowMatchSizeLg).matches) {
    store.dispatch('toggleSidebar', true)
  } else {
    store.dispatch('toggleSidebar', false)
  }
}

router.beforeEach((to, from, next) => {
  let isAuthRoute
  store.commit('setLoading', true)
  isAuthRoute = to.path.match('auth') !== null
  if (Vue.cookie.get('token')) {
    store.dispatch('setAuth', {
      isAuthed: true,
      token: Vue.cookie.get('token')
    })
  } else {
    store.dispatch('setAuth', {
      isAuthed: false
    })
  }
  if (!isAuthRoute && !store.state.ifr.isAuthed) {
    next('/auth/login')
  } else if (isAuthRoute && store.state.ifr.isAuthed) {
    next('/dashboard')
    if (from.path === '/dashboard') {
      store.commit('setLoading', false)
    }
  } else {
    next()
  }
}
)

router.afterEach((to, from) => {
  mediaHandler()
  store.commit('setLoading', false)
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App />',
  components: { App }
})
