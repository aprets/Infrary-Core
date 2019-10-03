<template xmlns:>
  <div class="form-wizard-page">
    <div class="row">
      <div class="col-md-12">
        <vuestic-widget class="no-h-padding" headerText="Server Creation Wizard">
          <vuestic-wizard
            :doVerifyLastStep="true"
            :steps="wizardSteps">

            <div slot="provider" class="form-wizard-tab-content">

              <p>
                Select a provider to provision the server with. <br>
                This can ether be one of the supported IaaS services or your own server. <br>
                Check the docs for instructions on how to get the API key from your provider. <br>
              </p>

              <div class="radio abc-radio abc-radio-primary">
                <input type="radio" name="radio1" id="radio1" value="DO" v-model="provider">
                <label for="radio1">
                  <span class="abc-label-text">Digital Ocean</span>
                </label>
              </div>

              <div class="radio abc-radio abc-radio-primary">
                <input type="radio" name="radio1" id="radio2" value="VT" v-model="provider" disabled>
                <label for="radio2">
                  <span class="abc-label-text">Vultr</span>
                </label>
              </div>

              <div class="radio abc-radio abc-radio-primary">
                <input type="radio" name="radio3" id="radio3" value="BYO" v-model="provider" disabled>
                <label for="radio3">
                  <span class="abc-label-text">BYO</span>
                </label>
              </div>

              <div v-show='isDo' class="form-group with-icon-right"
                   :class="{'has-error': errors.has('doToken'), 'valid': isFormFieldValid('doToken')}">
                <div class="input-group">
                  <input
                    name="doToken"
                    v-model="doToken"
                    v-validate="'required'"
                    data-vv-as="API token"
                    required title=""/>
                  <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
                  <i class="fa fa-check valid-icon icon-right input-icon"></i>
                  <label class="control-label">Digital Ocean API token</label><i class="bar"></i>
                  <small v-show="errors.has('doToken')" class="help text-danger">{{ errors.first('doToken') }}</small>
                </div>
              </div>
            </div>

            <div slot="properties" class="form-wizard-tab-content">
              <p>
                Select all the desired server properties. <br>
                A server with those properties will be created with your
                provider using the API key you specified (on your account). <br>
                You will have full control to stop or remove
                the server at any time. <br>
                The provider will bill you for the server directly, as usual.
              </p>

              <div class="form-group with-icon-right"
                   :class="{'has-error': errors.has('doServerName'), 'valid': isFormFieldValid('doServerName')}">
                <div class="input-group">
                  <input
                    name="doServerName"
                    v-model="doServerName"
                    v-validate="'required'"
                    data-vv-as="server name"
                    required title=""/>
                  <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
                  <i class="fa fa-check valid-icon icon-right input-icon"></i>
                  <label class="control-label">Server Name</label><i class="bar"></i>
                  <small v-show="errors.has('doServerName')" class="help text-danger">{{ errors.first('doServerName')
                    }}
                  </small>
                </div>
              </div>

              <vuestic-simple-select
                label="Server plan/size"
                v-model="doServerSlug"
                v-bind:options="doSizeList">
              </vuestic-simple-select>

              <vuestic-simple-select
                label="Server image"
                v-model="doServerImage"
                v-bind:options="doImageList">
              </vuestic-simple-select>

              <vuestic-simple-select
                label="Server region"
                v-model="doServerLocation"
                v-bind:options="doLocationList">
              </vuestic-simple-select>

              <div class="form-group with-icon-right"
                   :class="{'has-error': errors.has('doServerKey'), 'valid': isFormFieldValid('doServerKey')}">
                <div class="input-group">
                  <textarea
                    name="doServerKey"
                    v-model="doServerKey"
                    v-validate="'required'"
                    data-vv-as="ssh key"
                    required title="">
                  </textarea>
                  <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
                  <i class="fa fa-check valid-icon icon-right input-icon"></i>
                  <label class="control-label">SSH Public Key</label><i class="bar"></i>
                  <small v-show="errors.has('doServerKey')" class="help text-danger">{{ errors.first('doServerKey') }}
                  </small>
                </div>
              </div>

            </div>


            <div slot="configuration" class="form-wizard-tab-content">
              <p>
                Select all the desired server properties. <br>
                A server with those properties will be created with your
                provider using the API key you specified (on your account). <br>
                You will have full control to stop or remove
                the server at any time. <br>
                The provider will bill you for the server directly, as usual.
              </p>

              <div class="abc-checkbox abc-checkbox-primary">
                <input id="isMasterCheckbox" type="checkbox" v-model="doIsMaster">
                <label for="isMasterCheckbox">
                  <span class="abc-label-text">This is a master server</span>
                </label>
              </div>

              <div v-if="doIsMaster" class="abc-checkbox abc-checkbox-primary">
                <input id="isCustomMasterCheckbox" type="checkbox" v-model="doIsCustomMaster">
                <label for="isCustomMasterCheckbox">
                  <span class="abc-label-text">Use custom rancher setup commands</span>
                </label>
              </div>

              <div class="abc-checkbox abc-checkbox-primary">
                <input id="selfDestructCheckbox" type="checkbox" v-model="doSelfDestruct">
                <label for="selfDestructCheckbox">
                  <span class="abc-label-text">Self destruct server after creation (testing)</span>
                </label>
              </div>

              <div v-if="!doIsMaster || (doIsMaster && doIsCustomMaster)" class="cmd-list">

                <h5>Command list</h5>

                <p>
                  List of commands to be executed on server configuration (in order). <br>
                  Commands are executed natively, so you can set variables, create files etc. <br>
                  Hint: Use Enter, Backspace and arrow keys to create, navigate the fields
                </p>

                <div class="wizard-body-actions">
                  <div class="btn-container">
                    <button class="btn btn-secondary btn-micro pull-left" @click="addCommand">
                      Add
                    </button>
                  </div>

                  <div v-show="doCommandList.length > 1" class="btn-container">
                    <button class="btn btn-secondary btn-micro pull-right" @click="removeCommand">
                      Remove
                    </button>
                  </div>

                </div>

                <div v-for="(command, index) in doCommandList" class="form-group">
                  <div class="input-group">
                    <input
                      :ref="'commandField'"
                      v-bind:id="index"
                      v-model="doCommandList[index]"
                      @keydown.enter="addCommandKey"
                      @keydown.delete="removeCommandIfEmpty"
                      @keydown.38="upCommand"
                      @keydown.40="downCommand"
                      required/>
                    <i class="bar"></i>
                  </div>
                </div>

              </div>


            </div>
            <div slot="confirm" class="form-wizard-tab-content">
              <h4>Confirm selection</h4>
              <p>
                Make sure that the configuration shown is the desired one. <br>
                You can go back and alter it if needed.
              </p>
              <div class="table-responsive">
                <table class="table first-td-padding">
                  <tbody>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Provider: </span></td>
                    <td>{{provider}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">API Key: </span></td>
                    <td>{{doToken}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Server Name: </span></td>
                    <td>{{doServerName}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Server Size Slug: </span></td>
                    <td>{{doServerSlug}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Server Image: </span></td>
                    <td>{{doServerImage}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Server Region: </span></td>
                    <td>{{doServerLocation}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Server Public Key: </span></td>
                    <td>
                      <pre style="width: 30rem">{{doServerKey}}</pre>
                    </td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Is Server Master: </span></td>
                    <td>{{doIsMaster}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Is Server Self Destructing: </span></td>
                    <td>{{doSelfDestruct}}</td>
                  </tr>
                  <tr>
                    <td><span class="font-weight-bold vue-green-text">Server Configuration Command List: </span></td>
                    <td>
                      <pre style="width: 30rem">{{doProcessedCommandList}}</pre>
                    </td>
                  </tr>
                  </tbody>
                </table>
              </div>

            </div>
            <div slot="wizardCompleted" class="form-wizard-tab-content">
              <h4>Server creation started!</h4>
              <p>
                It can take a few minutes to provision, configure and start the server. <br>
                You can monitor its status in the dashboard.
              </p>
            </div>
          </vuestic-wizard>
        </vuestic-widget>
      </div>
    </div>
  </div>
</template>

<script>

  export default {
    name: 'server-create',
    data () {
      return {
        doMeta: {},
        wizardSteps: [
          {
            label: 'Provider',
            slot: 'provider',
            onNext: () => {
              this.validateFormField('doToken')
            },
            isValid: () => {
              if (!this.isFormFieldValid('doToken')) {
                return false
              }
              if (Object.keys(this.doMeta).length === 0 && this.doMeta.constructor === Object) {
                this.$store.commit('setLoading', true)
                this.getDoServerData()
                return false
              } else {
                return true
              }
            }
          },
          {
            label: 'Properties',
            slot: 'properties',
            onNext: () => {
              this.validateFormField('doServerName')
              this.validateFormField('doServerKey')
            },
            isValid: () => {
              return this.isFormFieldValid('doServerName') &&
                this.isFormFieldValid('doServerKey')
            }
          },
          {
            label: 'Configuration',
            slot: 'configuration',
            onNext: () => {
            },
            isValid: () => {
              return true
            }
          },
          {
            label: 'Confirm',
            slot: 'confirm',
            isValid: () => {
              if (!this.submittedServer) {
                this.$store.commit('setLoading', true)
                this.postServerData()
                return false
              } else {
                return true
              }
            }
          }
        ],
        provider: 'DO',
        doToken: 'a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6',
        doServerSlug: 's-1vcpu-1gb',
        doServerName: 'Infrary',
        doServerImage: 'ubuntu-16-04-x64',
        doServerLocation: 'lon1',
        doServerKey: 'ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==',
        doIsMaster: false,
        doIsCustomMaster: false,
        doSelfDestruct: false,
        doCommandList: [
          'echo hi'
        ],
        submittedServer: false
      }
    },
    watch: {
      doIsMaster: 'isMasterClick'
    },
    computed: {
      doProcessedCommandList () {
        if (this.doIsMaster) {
          if (this.doIsCustomMaster) {
            return this.doCommandList
          } else {
            return []
          }
        } else {
          return this.doCommandList
        }
      },
      isDo () {
        return this.provider === 'DO'
      },
      doSizeList () {
        let list = []
        for (let size in this.doMeta['sizes']) {
          if (this.doMeta['sizes'][size].available) {
            list.push(this.doMeta['sizes'][size]['slug'])
          }
        }
        return list
      },
      doImageList () {
        let list = []
        for (let image in this.doMeta['images']) {
          list.push(this.doMeta['images'][image]['slug'])
        }
        return list
      },
      doLocationList () {
        let list = []
        if (this.doMeta['images'] && this.doServerImage) {
          let regionsArray = this.doMeta['images'].find(item => item['slug'] === this.doServerImage)['regions']
          if (regionsArray) {
            for (let location in regionsArray) {
              list.push(regionsArray[location])
            }
            return list
          }
        }
      }
    },
    mounted () {
      if (this.doToken !== '') {
        this.validateFormField('doToken')
      }
    },
    methods: {
      isFormFieldValid (field) {
        let isValid = false
        if (this.formFields[field]) {
          isValid = this.formFields[field].validated && this.formFields[field].valid
        }
        return isValid
      },
      validateFormField (fieldName) {
        this.$validator.validate(fieldName, this[fieldName])
      },
      getDoServerData () {
        if (this.doToken) {
          this.axios.get(`/servers/DO/meta?token=` + this.doToken)
            .then(response => {
              if (response.status === 200) {
                this.doMeta = response.data
                this.$root.$emit('wizardGoNext')
                this.$store.commit('setLoading', false)
              }
            })
            .catch(error => {
              this.$snotify.error(error.response.data, {
                timeout: 10000
              })
              if (error.response.status === 401) {
                this.$store.dispatch('setAuth', {
                  isAuthed: false
                })
                this.$router.push('/auth/login')
              }
              this.$store.commit('setLoading', false)
            })
        }
      },
      addCommand () {
        this.doCommandList.push('')
      },
      upCommand () {
        let element = document.activeElement
        let index = parseInt(element.id)
        if (this.$refs.commandField[index - 1]) {
          this.$refs.commandField[index - 1].focus()
        }
      },
      downCommand () {
        let element = document.activeElement
        let index = parseInt(element.id)
        if (this.$refs.commandField[index + 1]) {
          this.$refs.commandField[index + 1].focus()
        }
      },
      addCommandKey () {
        let element = document.activeElement
        let index = parseInt(element.id)
        if (element) {
          this.doCommandList.splice(index + 1, 0, '')
          this.$nextTick(() => {
            let input = this.$refs.commandField[index + 1]
            input.focus()
          })
        }
      },
      removeCommand () {
        this.doCommandList.pop()
      },
      removeCommandIfEmpty () {
        let element = document.activeElement
        let index = parseInt(element.id)
        if (this.doCommandList.length > 1 && element && !element.value) {
          this.doCommandList.splice(index, 1)
          this.$nextTick(() => {
            let input = this.$refs.commandField[index - 1]
            input.focus()
          })
        }
      },
      postServerData () {
        if (this.doToken) {
          this.axios.post('/servers/provision/create', {
            properties: {
              provider: this.provider,
              token: this.doToken,
              name: this.doServerName,
              size: this.doServerSlug,
              image: this.doServerImage,
              location: this.doServerLocation,
              ssh_key: this.doServerKey
            },
            configuration: {
              is_master: this.doIsMaster,
              self_destruct: this.doSelfDestruct,
              cmd_list: this.doProcessedCommandList
            }
          })
            .then(response => {
              if (response.status === 200) {
                this.submittedServer = true
                this.$root.$emit('wizardCompleteWizard')
                this.$store.commit('setLoading', false)
                setTimeout(() => {
                  this.$router.push('/dashboard')
                }, 5000)
              }
            })
            .catch(error => {
              this.$snotify.error(error.response.data, {
                timeout: 10000
              })
              if (error.response.status === 401) {
                this.$store.dispatch('setAuth', {
                  isAuthed: false
                })
                this.$router.push('/auth/login')
              }
              this.$store.commit('setLoading', false)
            })
        }
      },
      isMasterClick () {
        if (this.doIsMaster) {
          this.doCommandList = [
            'curl https://releases.rancher.com/install-docker/17.06.sh | sh', 'service ntp stop',
            'update-rc.d -f ntp remove', 'fallocate -l 4G /swapfile', 'chmod 600 /swapfile',
            'mkswap /swapfile', 'swapon /swapfile',
            'echo "/swapfile   none    swap    sw    0   0" >> /etc/fstab',
            'docker run -d --restart=unless-stopped -p 8080:8080 rancher/server', 'sleep 60'
          ]
        } else {
          this.doCommandList = [
            'echo hi'
          ]
        }
      }
    }
  }
</script>

<style lang="scss">
  @import "../../../sass/_variables.scss";
  @import "../../../../node_modules/bootstrap/scss/functions";
  @import "../../../../node_modules/bootstrap/scss/variables";
  @import "../../../../node_modules/bootstrap/scss/mixins/breakpoints";

  .widget.simple-vertical-wizard-widget {
    .widget-body {
      padding: 0 $widget-padding;
      @include media-breakpoint-down(sm) {
        padding: $widget-padding 0;
      }
    }
  }

  .form-wizard-page {
    .cmd-list {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .form-group {
      min-width: 200px;
      max-width: 600px;
      width: 80%;
    }
  }


</style>
