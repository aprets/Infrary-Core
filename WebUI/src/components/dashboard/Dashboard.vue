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
        <widget headerText="Servers" buttonText="NEW" buttonRoute="/auth/login">
          <div class="table-responsive">
            <table class="table table-striped table-sm color-icon-label-table">
              <thead>
              <tr>
                <td align="middle"></td>
                <td align="middle">ID</td>
                <td align="middle">Provider</td>
                <td align="middle">Name</td>
                <td align="middle">IP</td>
              </tr>
              </thead>
              <tbody>
              <tr v-for="server in this.servers" class="table-success">
                <td>
                  <span class="badge badge-pill badge-primary">UP</span>
                </td>
                <td align="middle">{{server.__Infrary__ID}}</td>
                <td align="middle">{{server.__Infrary__Provider}}</td>
                <td align="middle">{{server.name}}</td>
                <td align="middle">{{server.__Infrary__IP}}</td>
              </tr>
              </tbody>
            </table>
          </div>
        </widget>
      </div>
    </div>

  </div>
</template>

<script>
  import Widget from '../vuestic-components/vuestic-widget/VuesticWidget'

  export default {
    components: {
      Widget
    },
    name: 'dashboard',
    data () {
      return {
        apiData: {},
        servers: []
      }
    },
    created () {
      this.updateApiData()
    },
    methods: {
      updateApiData () {
        this.$store.commit('setLoading', true)
        this.axios.get('/servers')
          .then(response => {
            if (response.status === 200) {
              this.apiData = response.data
              this.updateTableData()
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
          })
      },
      updateTableData () {
        this.servers = this.apiData
        this.$store.commit('setLoading', false)
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


