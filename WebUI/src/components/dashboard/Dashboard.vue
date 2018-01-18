<template>
  <div class="dashboard">
    <!--<div class="row">-->
      <!--<div class="col-md-12">-->
        <!--&lt;!&ndash;<vuestic-alert type="success" :withCloseBtn="true">&ndash;&gt;-->
          <!--&lt;!&ndash;<span class="badge badge-pill badge-success">SUCCESS</span>&ndash;&gt;-->
          <!--&lt;!&ndash;You successfully read this important alert message.&ndash;&gt;-->
          <!--&lt;!&ndash;<i class="fa fa-close alert-close"></i>&ndash;&gt;-->
        <!--&lt;!&ndash;</vuestic-alert>&ndash;&gt;-->
      <!--</div>-->
    <!--</div>-->

    <!--<dashboard-info-widgets></dashboard-info-widgets>-->

    <!--<vuestic-widget class="no-padding no-v-padding">-->
      <!--<vuestic-tabs :names="['Data Visualization', 'Users & Members', 'Setup Profile', 'Features']" ref="tabs">-->
        <!--<div slot="Data Visualization">-->
          <!--<data-visualisation-tab></data-visualisation-tab>-->
        <!--</div>-->
        <!--<div slot="Users & Members">-->
          <!--<users-members-tab></users-members-tab>-->
        <!--</div>-->
        <!--<div slot="Setup Profile">-->
          <!--<setup-profile-tab></setup-profile-tab>-->
        <!--</div>-->
        <!--<div slot="Features">-->
          <!--<features-tab></features-tab>-->
        <!--</div>-->
      <!--</vuestic-tabs>-->
    <!--</vuestic-widget>-->

    <!--<dashboard-bottom-widgets></dashboard-bottom-widgets>-->

    <div class="row">
      <div class="col-md-12">
        <widget headerText="Servers" buttonText="NEW" buttonRoute="/servers/create">
          <div v-if="this.servers.length < 1" class="text-center">
            <h4>🙈 No servers here 🙉</h4>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-striped table-sm color-icon-label-table">
              <thead>
              <tr>
                <td align="middle"></td>
                <td align="middle">ID</td>
                <td align="middle">Provider</td>
                <td align="middle">Name</td>
                <td align="middle">IP</td>
                <td align="middle"></td>
              </tr>
              </thead>
              <tbody>
              <tr v-for="server in this.servers" v-bind:class="trClassGen(server)">
                <td>
                  <span v-if="server.__Infrary__Status === 'up'" class="badge badge-pill badge-primary">UP</span>
                  <span v-if="server.__Infrary__Status === 'down'" class="badge badge-pill badge-danger">DOWN</span>
                  <span v-if="server.__Infrary__Status === 'configuring'" class="badge badge-pill badge-warning">CONFIGURING</span>
                  <span v-if="server.__Infrary__Status === 'created'" class="badge badge-pill badge-warning">CREATED</span>
                </td>
                <td align="middle">{{server.__Infrary__ID}}</td>
                <td align="middle">{{server.__Infrary__Provider}}</td>
                <td align="middle">{{server.name}}</td>
                <td align="middle">{{server.__Infrary__IP}}</td>
                <td align="middle">
                  <button class="btn btn-primary btn-with-icon rounded-icon" @click="deleteClick(server)">
                    <div class="btn-with-icon-content">
                      <i class="ion-android-close ion"></i>
                    </div>
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </widget>
      </div>
    </div>

    <modal ref="modal" :okText="'DELETE'" :okClass="'btn btn-danger'" v-on:ok="deleteServer">
      <div slot="title">Destroy Server</div>
      <div class="text-center">
        Are you sure you want to permanently remove the server? <br>
        <span class="vue-highlighted-text">Any data on the server will be deleted!</span>
      </div>
    </modal>

  </div>
</template>

<script>
  import Widget from '../vuestic-components/vuestic-widget/VuesticWidget'
  import Modal from '../vuestic-components/vuestic-modal/VuesticModal'

  export default {
    components: {
      Widget,
      Modal
    },
    name: 'dashboard',
    data () {
      return {
        apiData: {},
        servers: [],
        dataFilled: false,
        deleteCallingServer: null
      }
    },
    created () {
      this.updateApiData()
      this.interval = setInterval(() => {
        this.updateApiData()
      }, 10000)
    },
    beforeDestroy () {
      clearInterval(this.interval)
    },
    methods: {
      updateApiData () {
        if (!this.dataFilled) {
          this.$store.commit('setLoading', true)
        }
        this.axios.get('/servers')
          .then(response => {
            if (response.status === 200) {
              console.log(response)
              this.apiData = response.data
              this.servers = this.apiData
              if (!this.dataFilled) {
                this.dataFilled = true
                this.$store.commit('setLoading', false)
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
              this.$store.dispatch('setAuth', {
                isAuthed: false
              })
              this.$router.push('/auth/login')
            }
          })
      },
      deleteClick (server) {
        this.deleteCallingServer = server
        this.$refs.modal.open()
      },
      deleteServer () {
        this.axios.delete('/servers/' + this.deleteCallingServer.__Infrary__Provider + '/' + this.deleteCallingServer.__Infrary__ID)
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
              this.$store.dispatch('setAuth', {
                isAuthed: false
              })
              this.$router.push('/auth/login')
            }
          })
      },
      trClassGen (server) {
        return {
          'table-success': server.__Infrary__Status === 'up',
          'table-danger': server.__Infrary__Status === 'down',
          'table-warning': server.__Infrary__Status === 'created' || server.__Infrary__Status === 'configuting'
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
  @import "../../sass/_variables.scss";

  .color-icon-label-table {
    td:first-child {
      width: 1rem;
    }
  }
</style>

<!--<script>-->
  <!--// import VuesticWidget from '../vuestic-components/vuestic-widget/VuesticWidget'-->
  <!--// import VuesticAlert from '../vuestic-components/vuestic-alert/VuesticAlert'-->
  <!--// import DashboardInfoWidgets from './DashboardInfoWidgets'-->
  <!--// import VuesticTabs from '../vuestic-components/vuestic-tabs/VuesticTabs.vue'-->
  <!--// import UsersMembersTab from './users-and-members-tab/UsersMembersTab.vue'-->
  <!--// import SetupProfileTab from './setup-profile-tab/SetupProfileTab.vue'-->
  <!--// import FeaturesTab from './features-tab/FeaturesTab.vue'-->
  <!--// import DataVisualisationTab from './data-visualisation-tab/DataVisualisation.vue'-->
  <!--// import DashboardBottomWidgets from './DashboardBottomWidgets.vue'-->
  <!--import Widget from '../vuestic-components/vuestic-widget/VuesticWidget'-->
  <!--import DataTable from '../vuestic-components/vuestic-datatable/VuesticDataTable'-->
  <!--import BadgeColumn from '../tables/BadgeColumn.vue'-->
  <!--import Vue from 'vue'-->
  <!--import FieldsDef from '../vuestic-components/vuestic-datatable/data/fields-definition'-->
  <!--import ItemsPerPageDef from '../vuestic-components/vuestic-datatable/data/items-per-page-definition'-->

  <!--Vue.component('badge-column', BadgeColumn)-->


  <!--export default {-->
    <!--name: 'dashboard',-->
    <!--components: {-->
      <!--components: {-->
        <!--DataTable,-->
        <!--Widget-->
      <!--}-->
    <!--},-->
    <!--data () {-->
      <!--return {-->
        <!--apiUrl: 'https://vuetable.ratiw.net/api/users',-->
        <!--apiMode: true,-->
        <!--tableFields: FieldsDef.tableFields,-->
        <!--itemsPerPage: ItemsPerPageDef.itemsPerPage,-->
        <!--sortFunctions: FieldsDef.sortFunctions,-->
        <!--paginationPath: ''-->
      <!--}-->
    <!--}-->
  <!--}-->
<!--</script>-->


