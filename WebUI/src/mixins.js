export default {
  methods: {
    checkAuth () {
      let tokenCookie = this.$cookie.get('token')
      if (tokenCookie) {
        this.$store.dispatch('setAuth', {
          isAuthed: true,
          token: tokenCookie
        })
      } else {
        this.$store.dispatch('setAuth', {
          isAuthed: false
        })
      }
    },
    logout () {
      this.setAuth({
        isAuthed: false
      })
      this.$router.push('/auth/login')
    },
    updateUserData () {
      this.axios.get('/user')
        .then(response => {
          if (response.status === 200) {
            console.log(response)
            this.setUserData(response.data)
          }
        })
        .catch((error) => {
          if (error.response) {
            this.$snotify.error(error.response.data)
          } else if (error.message) {
            this.$snotify.error('Unable to connect to API: ' + error.message)
          } else {
            this.$snotify.error(error)
          }
          if (error.response.status === 401) {
            this.logout()
          }
        })
    }
  }
}
