import Vue from 'vue'
import Vuex from 'vuex'
import VuexI18n from 'vuex-i18n' // load vuex i18n module

import menu from './modules/menu'
import app from './modules/app'
import ifr from './modules/ifr'

import * as getters from './getters'

Vue.use(Vuex)

const store = new Vuex.Store({
  strict: true, // process.env.NODE_ENV !== 'production',
  getters,
  modules: {
    menu,
    app,
    ifr
  },
  state: {},
  mutations: {}
})

Vue.use(VuexI18n.plugin, store)

export default store
