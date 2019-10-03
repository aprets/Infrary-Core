
// import statistics from './statistics'
// import forms from './forms'
// import ui from './ui'
// import maps from './maps'
// import tables from './tables'
// import extra from './extra'
import * as types from '../../mutation-types'
import dashboard from './dashboard'
import environment from './environment'
import auth from './auth'
import servers from './servers'
const state = {
  items: [
    auth,
    dashboard,
    environment,
    servers
  ]
}

const mutations = {
  [types.TOGGLE_EXPAND_MENU_ITEM] (state, payload) {
    let menuItem = payload.menuItem
    let expand = payload.expand
    if (menuItem.children && menuItem.meta) {
      menuItem.meta.expanded = expand
    }
  }
}

const actions = {
  toggleExpandMenuItem ({commit}, payload) {
    commit(types.TOGGLE_EXPAND_MENU_ITEM, payload)
  }
}

export default {
  state,
  mutations,
  actions
}
