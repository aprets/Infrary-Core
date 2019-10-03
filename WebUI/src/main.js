// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import VeeValidate from 'vee-validate'
import App from './App'
import store from './store'
import router from './router'
import {sync} from 'vuex-router-sync'
import VuesticPlugin from 'vuestic-theme/vuestic-plugin'
import './i18n'
import axios from 'axios'
import VueClipboard from 'vue-clipboard2'
import VueAxios from 'vue-axios'
import Snotify from 'vue-snotify'
import 'vue-snotify/styles/material.css' // or dark.css or simple.css
import VueCookie from 'vue-cookie'
import VueTextareaAutosize from 'vue-textarea-autosize'

Vue.use(VueTextareaAutosize)
Vue.use(VueClipboard)
Vue.use(VueCookie)
Vue.use(Snotify)
Vue.use(VueAxios, axios)
Vue.use(VuesticPlugin)


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
  let tokenCookie = VueCookie.get('token')
  if (tokenCookie) {
    store.dispatch('setAuth', {
      isAuthed: true,
      token: tokenCookie
    })
  } else {
    store.dispatch('setAuth', {
      isAuthed: false
    })
  }
  let isAuthRoute
  store.commit('setLoading', true)
  isAuthRoute = to.path.match('auth') !== null
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
  template: '<App/>',
  components: {App}
})
