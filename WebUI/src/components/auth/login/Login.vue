<template>
  <div class="login">
    <h2 v-if="isFromSignup">Welcome!</h2>
    <h2 v-else>Login</h2>
    <vuestic-alert v-if="isFromSignup" type="warning" :withCloseBtn="true">
      Please verify your email to finish account creation.
    </vuestic-alert>
    <vuestic-alert v-if="isEmailKeySuccess" type="success" :withCloseBtn="true">
      Email successfully verified!
    </vuestic-alert>
    <vuestic-alert v-if="isEmailKeyFail" type="danger" :withCloseBtn="true">
      Email verification failed!
    </vuestic-alert>
    <form v-on:submit.prevent="onSubmit" method="post" action="/auth/login" name="login">
      <div class="form-group with-icon-right" :class="{'has-error': errors.has('email'), 'valid': isEmailValid}">
        <div class="input-group">
          <input
            id="email"
            name="email"
            v-model="email"
            v-validate="'required|email'"
            required/>
          <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
          <i class="fa fa-check valid-icon icon-right input-icon"></i>
          <label class="control-label" for="email">Email</label><i class="bar"></i>
          <small v-show="errors.has('email')" class="help text-danger">
            {{ errors.first('email') }}
          </small>
        </div>
      </div>
      <div class="form-group with-icon-right" :class="{'has-error': errors.has('password'), 'valid': isPasswordValid}">
        <div class="input-group">
          <input
            id="password"
            name="password"
            type="password"
            v-model="password"
            v-validate="'required|alpha'"
            required/>
          <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
          <i class="fa fa-check valid-icon icon-right input-icon"></i>
          <label class="control-label" for="password">Password</label><i class="bar"></i>
          <small v-show="errors.has('password')" class="help text-danger">
            {{ errors.first('password') }}
          </small>
        </div>
      </div>
      <div class="d-flex flex-column flex-lg-row align-items-center justify-content-between down-container">
        <button class="btn btn-primary" type="submit">
          Log In
        </button>
        <router-link class='link' :to="{name: 'Signup'}">Create account</router-link>
      </div>
    </form>
  </div>
</template>

<script>
  import _ from 'lodash'

  export default {
    name: 'login',
    data () {
      return {
        email: 'tpk1100@gmail.com',
        password: 'qwertyui',
        isEmailKeySuccess: false,
        isEmailKeyFail: false
      }
    },
    computed: {
      isFromSignup () {
        return this.$store.state.ifr.isVerifyingEmail
      },
      isEmailValid () {
        return this.isFieldValid('email')
      },
      isPasswordValid () {
        return this.isFieldValid('password')
      }
    },
    created () {
      if (this.$route.query.emailKey) {
        this.axios.post('/auth/verify', {
          emailKey: this.$route.query.emailKey
        })
          .then(response => {
            if (response.status === 201) {
              this.$store.state.ifr.isVerifyingEmail = false
              this.isEmailKeySuccess = true
              this.isEmailKeyFail = false
            }
          })
          .catch(error => {
            this.isEmailKeySuccess = false
            this.isEmailKeyFail = true
            this.$snotify.error(error.response.data, {
              timeout: 10000
            })
          })
      }
    },
    methods: {
      isFieldValid (aField) {
        let isValid = false
        if (this.formFields[aField]) {
          isValid = this.formFields[aField].validated && this.formFields[aField].valid
        }
        return isValid
      },
      onSubmit: _.throttle(function () {
        this.isEmailKeySuccess = false
        this.isEmailKeyFail = false
        this.$validator.validateAll().then((result) => {
          if (result) {
            this.axios.post('/auth/login', {
              email: this.email,
              password: this.password
            })
              .then(response => {
                if (response.status === 200) {
                  this.$store.dispatch('setAuth', {
                    isAuthed: true,
                    token: response.data,
                    setCookie: true
                  })
                  this.$router.push('/dashboard')
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
            return
          }

          this.$snotify.error('Invalid form')
        })
      }, 5000)
    }
  }
</script>

<style lang="scss">
  @import '../../../sass/variables';
  @import '../../../../node_modules/bootstrap/scss/mixins/breakpoints';
  @import '../../../../node_modules/bootstrap/scss/variables';
  .login {
    @include media-breakpoint-down(md) {
      width: 100%;
      padding-right: 2rem;
      padding-left: 2rem;
      .down-container {
        .link {
          margin-top: 2rem;
        }
      }
    }

    h2 {
      text-align: center;
    }
    width: 21.375rem;

    .down-container {
      margin-top: 3.125rem;
    }
  }
</style>
