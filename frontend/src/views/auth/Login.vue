<template>
  <form action="" class="form" @submit.prevent="login">
    <div class="mb-3">
      <label for="username" class="form-label">Email</label>
      <input type="email" class="form-control" id="username" placeholder="Email" v-model="username" />
    </div>
    <div class="mb-3">
      <label for="password" class="form-label">Password</label>
      <input type="password" class="form-control" id="password" placeholder="Password" v-model="password" />
    </div>
    <button type="submit" class="btn btn-primary w-100 mb-3">login</button>
    <router-link to="/forget-password" class="d-block mb-3">Forget Password?</router-link>
    <router-link to="/register">Register</router-link>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')

const login = () => {
  console.log('login', username.value, password.value)
}
</script>

<style lang="scss" scoped></style>
