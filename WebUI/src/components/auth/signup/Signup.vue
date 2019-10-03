<template>
  <div class="signup">
    <h2>Create New Account</h2>
    <form v-on:submit.prevent="onSubmit" method="post" action="/auth/signup" name="signup">
      <div class="form-group with-icon-right"
           :class="{'has-error': errors.has('first_name'), 'valid': isFirstNameValid}">
        <div class="input-group">
          <input
            id="first_name"
            name="first_name"
            data-vv-as="first name"
            v-model="first_name"
            v-validate="'required|alpha'"
            required/>
          <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
          <i class="fa fa-check valid-icon icon-right input-icon"></i>
          <label class="control-label" for="first_name">First name</label><i class="bar"></i>
          <small v-show="errors.has('first_name')" class="help text-danger">
            {{ errors.first('first_name') }}
          </small>
        </div>
      </div>
      <div class="form-group with-icon-right" :class="{'has-error': errors.has('last_name'), 'valid': isLastNameValid}">
        <div class="input-group">
          <input
            id="last_name"
            name="last_name"
            data-vv-as="last name"
            v-model="last_name"
            v-validate="'required|alpha'"
            required/>
          <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
          <i class="fa fa-check valid-icon icon-right input-icon"></i>
          <label class="control-label" for="last_name">Last name</label><i class="bar"></i>
          <small v-show="errors.has('last_name')" class="help text-danger">
            {{ errors.first('last_name') }}
          </small>
        </div>
      </div>
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
            v-validate="'required|min:8'"
            required/>
          <i class="fa fa-exclamation-triangle error-icon icon-right input-icon"></i>
          <i class="fa fa-check valid-icon icon-right input-icon"></i>
          <label class="control-label" for="password">Password</label><i class="bar"></i>
          <small v-show="errors.has('password')" class="help text-danger">
            {{ errors.first('password') }}
          </small>
        </div>
      </div>
      <div class="abc-checkbox abc-checkbox-primary">
        <input
          id="checkbox"
          name="checkbox"
          data-vv-as="Terms of Use"
          type="checkbox"
          v-validate="'required'"
          required
          checked>
        <label for="checkbox">
          <span class="abc-label-text">I agree to <router-link to="">Terms of Use.</router-link></span>
        </label><br>
        <small v-show="errors.has('checkbox')" class="help text-danger">
          {{ errors.first('checkbox') }}
        </small>
      </div>
      <div class="d-flex flex-column flex-lg-row align-items-center justify-content-between down-container">
        <button class="btn btn-primary" type="submit">
          Sign Up
        </button>
        <router-link class='link' :to="{name: 'Login'}">Already joined?</router-link>
      </div>
    </form>
  </div>
</template>

<script>
  import _ from 'lodash'

  export default {
    name: 'signup',
    data: () => ({
      first_name: 'Bobby',
      last_name: 'D',
      password: 'qwertyui',
      email: 'tpk1100@gmail.com'
    }),
    computed: {
      isFirstNameValid () {
        return this.isFieldValid('first_name')
      },
      isLastNameValid () {
        return this.isFieldValid('last_name')
      },
      isEmailValid () {
        return this.isFieldValid('email')
      },
      isPasswordValid () {
        return this.isFieldValid('password')
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
        this.$validator.validateAll().then((result) => {
          if (result) {
            this.axios.post('/auth/register', {
              first_name: this.first_name,
              last_name: this.last_name,
              email: this.email,
              password: this.password
            })
              .then(response => {
                if (response.status === 201) {
                  this.$store.state.ifr.isVerifyingEmail = true
                  this.$router.push('/auth/login')
                }
              })
              .catch(error => {
                this.$snotify.error(error.response.data)
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
  @import "../../../../node_modules/bootstrap/scss/functions";
  @import '../../../../node_modules/bootstrap/scss/variables';

  .signup {
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
      margin-top: 2.6875rem;
    }
  }
</style>
