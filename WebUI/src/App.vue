<template>
  <div id="app" class="app">
    <auth-layout  v-if="!isAuthed"></auth-layout>
    <layout v-else></layout>
    <vue-snotify></vue-snotify>
  </div>
</template>

<script>
  import Layout from 'components/layout/Layout'
  import AuthLayout from 'components/layout/AuthLayout'
  import VuesticPreLoader from 'vuestic-components/vuestic-preloader/VuesticPreLoader.vue'
  import mixin from './mixins'

  export default {
    name: 'app',
    mixins: [mixin],
    components: {
      VuesticPreLoader,
      AuthLayout,
      Layout
    },
    computed: {
      isAuthed () {
        return this.$store.state.ifr.isAuthed
      }
    },
    created () {
      this.checkAuth()
      this.axios.defaults.baseURL = this.$store.state.ifr.apiUrl
      this.axios.defaults.headers.post['Content-Type'] = 'application/json'
    }
  }
</script>

<style lang="scss">
  @import "sass/main";
  body {
    height: 100%;
    .app {
      height: 100%;
    }
  }
</style>
