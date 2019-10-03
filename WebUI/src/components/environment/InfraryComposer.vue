<template>
  <div class="row">
    <div class="col-md-12">
      <vuestic-widget :headerText="'Infrary Compose'">
        <!--UPLOAD-->
        <div class="dropbox">
          <input type="file" @change="filesChange" class="input-file">
          <p>
            Drag your infrary-compose here or click to browse
          </p>
        </div>
        <div class="form-group">
          <div class="input-group">
            <textarea-autosize placeholder="You can also pate or type your infra-conf contents here..."
                               v-model="composeData"></textarea-autosize>
          </div>
        </div>
        <div class="d-flex  justify-content-center">
          <button :disabled="!composeData.length"  @click="submitData" class="btn btn-primary">
            SUBMIT
          </button>
        </div>

      </vuestic-widget>
    </div>
  </div>


</template>

<script>
  export default {
    name: 'infrary-composer',

    data () {
      return {
        composeData: 'version: \'0\'\n' +
        'servers:\n' +
        '    slave:\n' +
        '        properties:\n' +
        '            provider: DO\n' +
        '            token: a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6\n' +
        '            size: 512mb\n' +
        '            image: ubuntu-14-04-x64\n' +
        '            location: lon1\n' +
        '            ssh_key: ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==\n' +
        '            \n' +
        '        configuration:\n' +
        '            is_master: false\n' +
        '            self_destruct: false\n' +
        '            cmd_list: [\'echo hi\']\n' +
        '    slave2:\n' +
        '        properties:\n' +
        '            provider: DO\n' +
        '            token: a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6\n' +
        '            size: 512mb\n' +
        '            image: ubuntu-14-04-x64\n' +
        '            location: lon1\n' +
        '            ssh_key: ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==\n' +
        '            \n' +
        '        configuration:\n' +
        '            is_master: false\n' +
        '            self_destruct: false\n' +
        '            cmd_list: [\'echo hi\']\n' +
        '    slave3:\n' +
        '        properties:\n' +
        '            provider: DO\n' +
        '            token: a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6\n' +
        '            size: 512mb\n' +
        '            image: ubuntu-14-04-x64\n' +
        '            location: lon1\n' +
        '            ssh_key: ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==\n' +
        '            \n' +
        '        configuration:\n' +
        '            is_master: false\n' +
        '            self_destruct: false\n' +
        '            cmd_list: [\'echo hi\']\n' +
        '    slave4:\n' +
        '        properties:\n' +
        '            provider: DO\n' +
        '            token: a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6\n' +
        '            size: 512mb\n' +
        '            image: ubuntu-14-04-x64\n' +
        '            location: lon1\n' +
        '            ssh_key: ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==\n' +
        '            \n' +
        '        configuration:\n' +
        '            is_master: false\n' +
        '            self_destruct: false\n' +
        '            cmd_list: [\'echo hi\']\n' +
        '    master:\n' +
        '        properties:\n' +
        '            provider: DO\n' +
        '            token: a7e26ca2837730e171e367dca448252a2e40015aab140079a866ba95996db4c6\n' +
        '            size: 512mb\n' +
        '            image: ubuntu-14-04-x64\n' +
        '            location: lon1\n' +
        '            ssh_key: ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3KVkFiPI+5RlTiTKsRkjEZr6ssjYFw9Tk0dzoLKYQH8NOWA13tpSo8r6wT7P+yxXG631wGSBfHyarCpuNO8X2sS7y1zWFVIiDvp1cT4sKGF3kfMPjmt5vrfrp+qEzxHDG9oQqCvnYv1NnhIsb+ZgLG+S56z7ssEx+CPpbUU2RE+27/RYxRNjSZQ7l3eNiQyyvBlPBnK+RK6uccUJhG8KfqWB1hOtlJ7H71Mx0RwiLA6as7OK5PuwqkCN5JhzJs48mRjtRE86R0VwKwny/LuPmTMyyz7JCg38C4PDgEXIJrAfuo/TJDcqiJnxPeX4+neDnmXEeVvUqMUnbVNlk8qZ+w==\n' +
        '            \n' +
        '        configuration:\n' +
        '            is_master: true\n' +
        '            self_destruct: false\n' +
        '            cmd_list: []\n' +
        'stacks:\n' +
        '    teststack:\n' +
        '        docker-compose:\n' +
        '            version: \'2\'\n' +
        '            services:\n' +
        '              what:\n' +
        '                image: ubuntu:14.04.3\n' +
        '                stdin_open: true\n' +
        '                tty: true\n' +
        '                command:\n' +
        '                - /bin/bash\n' +
        '                labels:\n' +
        '                  io.rancher.container.pull_image: always\n' +
        '              test:\n' +
        '                image: ubuntu:14.04.3\n' +
        '                environment:\n' +
        '                  a: b\n' +
        '                stdin_open: true\n' +
        '                tty: true\n' +
        '                ports:\n' +
        '                - 555:65535/tcp\n' +
        '                command:\n' +
        '                - /bin/bash\n' +
        '                labels:\n' +
        '                  io.rancher.container.pull_image: always\n' +
        '                  io.rancher.scheduler.global: \'true\'\n' +
        '        rancher-compose:\n' +
        '            version: \'2\'\n' +
        '            services:\n' +
        '              what:\n' +
        '                scale: 1\n' +
        '                start_on_create: true\n' +
        '              test:\n' +
        '                start_on_create: true  \n' +
        '    otherstack:\n' +
        '        docker-compose:\n' +
        '            version: \'2\'\n' +
        '            services:\n' +
        '              what:\n' +
        '                image: ubuntu:14.04.3\n' +
        '                stdin_open: true\n' +
        '                tty: true\n' +
        '                command:\n' +
        '                - /bin/bash\n' +
        '                labels:\n' +
        '                  io.rancher.container.pull_image: always\n' +
        '              test:\n' +
        '                image: ubuntu:14.04.3\n' +
        '                environment:\n' +
        '                  a: b\n' +
        '                stdin_open: true\n' +
        '                tty: true\n' +
        '                ports:\n' +
        '                - 555:65535/tcp\n' +
        '                command:\n' +
        '                - /bin/bash\n' +
        '                labels:\n' +
        '                  io.rancher.container.pull_image: always\n' +
        '                  io.rancher.scheduler.global: \'true\'\n' +
        '        rancher-compose:\n' +
        '            version: \'2\'\n' +
        '            services:\n' +
        '              what:\n' +
        '                scale: 1\n' +
        '                start_on_create: true\n' +
        '              test:\n' +
        '                start_on_create: true  \n' +
        '          '
      }
    },

    methods: {
      filesChange (event) {
        // Reference to the DOM input element
        let input = event.target
        // Ensure that you have a file before attempting to read it
        if (input.files && input.files[0]) {
          let reader = new FileReader()
          // Define a callback function to run, when FileReader finishes its job
          reader.onload = (e) => {
            this.composeData = e.target.result
          }
          // Start the reader job - read file as text
          if (input.files[0].size <= 100000) {
            reader.readAsText(input.files[0])
          } else {
            this.$snotify.error('File too large!')
          }
        }
      },
      submitData () {
        this.axios.post('/infrary-compose', {
          'infrary-compose': btoa(this.composeData)
        })
          .then(response => {
            if (response.status === 200) {
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
      }
    }
  }
</script>

<style lang="scss">
  @import "../../sass/_variables.scss";

  $dotted-line-offset: 10px;
  $box-height: 100px;

  .dropbox {
    outline: 2px dashed grey; /* the dash box */
    outline-offset: -$dotted-line-offset;
    background: $light-green;
    color: $vue-darkest-blue;
    padding: $dotted-line-offset;
    min-height: $box-height; /* minimum height */
    position: relative;
    cursor: pointer;
  }

  .input-file {
    opacity: 0; /* invisible but it's there! */
    width: calc(100% - 2 * #{$dotted-line-offset});
    height: $box-height - 2*$dotted-line-offset;
    position: absolute;
    cursor: pointer;
  }

  .dropbox:hover {
    background: lightgreen; /* when mouse over to the drop zone, change color */
  }

  .dropbox p {
    font-size: 1.2em;
    text-align: center;
    padding: $box-height/4 0 0 0;
  }

</style>
