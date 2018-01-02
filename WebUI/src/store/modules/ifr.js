import Vue from 'vue'

const state = {
  isVerifyingEmail: false,
  isAuthed: false,
  apiUrl: 'http://127.0.0.1:5000/v0/',
  apiToken: ''
}

const mutations = {
  setLoading (state, isLoading) {
    state.isLoading = isLoading
  },
  setIsAuthed (state, isAuthed) {
    state.isAuthed = isAuthed
  },
  setApiToken (state, apiToken) {
    state.apiToken = apiToken
  }
}

const actions = {
  setAuth ({ commit }, payload) {
    if (payload.isAuthed) {
      Vue.axios.defaults.headers.common['Authorization'] = `Bearer ${payload.token}`
      if (payload.setCookie) {
        Vue.cookie.set('token', payload.token, { expires: '1h' })
      }
    } else {
      Vue.cookie.delete('token')
      Vue.axios.defaults.headers.common['Authorization'] = ''
    }
    commit('setIsAuthed', payload.isAuthed)
    commit('setApiToken', payload.token)
  }
}

export default {
  state,
  mutations,
  actions
}
