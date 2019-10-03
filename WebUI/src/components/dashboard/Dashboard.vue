<template>
  <div class="dashboard">
    <div class="row">
      <div class="col-md-12">
        <vuestic-widget headerText="Servers" buttonText="NEW" buttonRoute="/servers/create">
          <div v-if="this.servers.length < 1" class="text-center">
            <h4>🙈 No servers here 🙉</h4>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-striped table-sm color-icon-label-table">
              <thead>
              <tr>
                <td align="middle">Tags</td>
                <td align="middle">ID</td>
                <td align="middle">Provider</td>
                <!--<td align="middle">Name</td>-->
                <td align="middle">IP</td>
                <td align="middle">Actions</td>
              </tr>
              </thead>
              <tbody>
              <tr v-for="server, server_index in this.servers" v-bind:class="trClassGen(server)">
                <td align="middle">
                  <span v-if="server.status === 'up'" class="badge badge-pill badge-primary">UP</span>
                  <span v-if="server.status === 'down'" class="badge badge-pill badge-danger">DOWN</span>
                  <span v-if="server.status === 'configuring'" class="badge badge-pill badge-warning">CONFIGURING</span>
                  <span v-if="server.status === 'created'" class="badge badge-pill badge-warning">CREATED</span><br>
                  <span v-if="server.is_master === true" class="badge badge-pill badge-info">MASTER</span>
                </td>
                <td align="middle">{{server.id}}</td>
                <td align="middle">{{server.provider}}</td>
                <!--<td align="middle">{{server.name}}</td>-->
                <td v-if="server.is_master === true && server.status === 'up'" align="middle"><a class="vue-green-text"
                                                                       :href="'http://' + server.ip + ':8080'"
                                                                       target="_blank">{{server.ip}}</a></td>
                <td v-else align="middle">{{server.ip}}</td>
                <td align="center">
                  <button v-if="server.is_master === true && server.status === 'up'" title="Show Credentials"
                          class="btn btn-primary btn-with-icon rounded-icon"
                          @click="updateUserData();$refs.credsModal.open()">
                    <div class="btn-with-icon-content creds-btn">
                      <i class="ion-md-contact ion"></i>
                    </div>
                  </button>
                  <button v-else title="" class="btn btn-with-icon rounded-icon fake-button"></button>
                  <button title="Show Log" class="btn btn-primary btn-with-icon rounded-icon"
                          @click="openLog(server_index)">
                    <div class="btn-with-icon-content log-btn">
                      <i class="ion-md-list-box ion"></i>
                    </div>
                  </button>
                  <button title="Delete" class="btn btn-primary btn-with-icon rounded-icon"
                          @click="deleteClick(server)">
                    <div class="btn-with-icon-content delete-btn">
                      <i class="ion-md-close ion"></i>
                    </div>
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </vuestic-widget>
      </div>
    </div>

    <vuestic-modal ref="deleteModal" :okText="'DELETE'" :okClass="'btn btn-danger'" v-on:ok="deleteServer">
      <div slot="title">Destroy Server</div>
      <div class="text-center">
        Are you sure you want to permanently remove the server? <br>
        <span class="vue-highlighted-text">Any data on the server will be deleted!</span>
        <br>
        <br>
        <div v-if="!isDeleteCallingServerUp" class="alert-danger">
          <b> SERVER IS NOT FULLY INITIALISED! <br> TRYING TO DELETE IT MIGHT LEAVE IT RUNNING ON YOUR ACCOUNT! </b>
        </div>
        <div v-if="isDeleteCallingServerMaster" class="alert-danger">
          <b> SERVER IS A MASTER! <br> THE ENVIRONMENT AND ALL THE SERVERS WILL BE DELETED WITH IT! </b>
        </div>
      </div>
    </vuestic-modal>

    <vuestic-modal ref="credsModal" :cancelClass="'none'" okText="close" :cancelText="''">
      <div slot="title">Master Credentials</div>
      <div>
        <i>Click on <a href="#" @click.prevent>green</a> text to copy</i><br><br>
        <b>Login:</b> <a href="#" @click.prevent="copyToClipboard(masterLogin)">{{this.masterLogin}}</a><br>
        <b>Password:</b> <a href="#" @click.prevent="copyToClipboard(masterPass)">{{this.masterPass}}</a>
      </div>
    </vuestic-modal>

    <vuestic-modal ref="logModal" v-bind:large="true" :cancelClass="'none'" okText="close" :cancelText="''">
      <div slot="title">Server Log</div>
      <div style="word-wrap: break-word" v-html="logText"></div>

    </vuestic-modal>


  </div>
</template>

<script>

  import {mapGetters, mapMutations, mapActions} from 'vuex'
  import mixin from '../../mixins.js'

  export default {
    name: 'dashboard',
    mixins: [mixin],
    data () {
      return {
        servers: [],
        dataFilled: false,
        deleteCallingServer: undefined,
        curServerIndex: {}
      }
    },
    computed: {
      ...mapGetters([
        'masterConf',
        'userData'
      ]),
      logText () {
        if (typeof this.servers[this.curServerIndex] !== 'undefined') {
          if (this.servers[this.curServerIndex] !== {}) {
            return this.servers[this.curServerIndex].log.replace(/\n/g, '<br />')
          }
        }
        return ''
      },
      isDeleteCallingServerUp () {
        if (typeof this.deleteCallingServer !== 'undefined') {
          if (this.deleteCallingServer !== {}) {
            return this.deleteCallingServer.status === 'up'
          }
        }
        return false
      },
      isDeleteCallingServerMaster () {
        if (typeof this.deleteCallingServer !== 'undefined') {
          if (this.deleteCallingServer !== {}) {
            return this.deleteCallingServer.is_master
          }
        }
        return false
      },
      masterLogin () {
        if (typeof this.userData.master_conf !== 'undefined') {
          if (typeof this.userData.master_conf.user !== 'undefined') {
            return this.userData.master_conf.user
          }
        }
        return ''
      },
      masterPass () {
        if (typeof this.userData.master_conf !== 'undefined') {
          if (typeof this.userData.master_conf.password !== 'undefined') {
            return this.userData.master_conf.password
          }
        }
        return ''
      }
    },
    created () {
      this.updateAPIData()
      this.interval = setInterval(() => {
        this.updateAPIData()
      }, 10000)
    },
    beforeDestroy () {
      clearInterval(this.interval)
    },
    methods: {
      ...mapMutations([
        'setMasterConf',
        'setLoading',
        'setUserData'
      ]),
      ...mapActions([
        'setAuth'
      ]),
      updateAPIData () {
        if (!this.dataFilled) {
          this.setLoading(true)
        }
        this.axios.get('/servers')
          .then(response => {
            if (response.status === 200) {
              console.log(response)
              this.servers = response.data
              if (!this.dataFilled) {
                this.dataFilled = true
                this.setLoading(false)
              }
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
              this.setAuth({
                isAuthed: false
              })
              this.$router.push('/auth/login')
            }
          })
      },
      deleteClick (server) {
        this.deleteCallingServer = server
        this.$refs.deleteModal.open()
      },
      deleteServer () {
        this.axios.delete('/servers/' + this.deleteCallingServer.provider + '/' + this.deleteCallingServer.id + '?force=true')
          .then(response => {
            if (response.status === 200) {
              console.log(response)
              this.$snotify.success(response.data)
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
              this.setAuth({
                isAuthed: false
              })
              this.$router.push('/auth/login')
            }
          })
      },
      trClassGen (server) {
        return {
          'table-success': server.status === 'up' && !server.is_master,
          'table-info': server.status === 'up' && server.is_master,
          'table-danger': server.status === 'down',
          'table-warning': server.status === 'created' || server.status === 'configuring'
        }
      },
      copyToClipboard (text) {
        this.$copyText(text).then(() => {
          this.$snotify.info('Copied to clipboard')
        }, () => {
          this.$snotify.error('Please use CTRL+C to copy')
        })
      },
      openLog (serverIndex) {
        this.curServerIndex = serverIndex
        this.$refs.logModal.open()
      }
    }
  }
</script>

<style lang="scss" scoped>
  @import "../../sass/_variables.scss";

  .log-btn i {
    left: 1rem !important;
  }

  .creds-btn i {
    left: 0.95rem !important;
  }

  .delete-btn i {
    left: 1.15rem !important;
  }

  .fake-button {
    background-color: transparent;
    cursor: default;
    opacity: 0;
  }

  .log {
    color: #34495e;
  }
</style>
