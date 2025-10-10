<template>
  <form action="" class="form" @submit.prevent="register">
    <div class="mb-3">
      <label for="username" class="form-label">Username</label>
      <input
        type="email"
        class="form-control"
        id="username"
        placeholder="Username"
        v-model="username"
      />
    </div>
    <div class="mb-3">
      <label for="password" class="form-label">Password</label>
      <input
        type="password"
        class="form-control"
        id="password"
        placeholder="Password"
        v-model="password"
      />
    </div>
    <button type="submit" class="btn btn-primary w-100 mb-3">Register</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api/service'

const username = ref('')
const password = ref('')

const register = () => {
  api
    .post('/user', {
      username: username.value,
      password: password.value,
      is_superuser: true,
    })
    .then((response) => {
      console.log(response)
    })
    .catch((error) => {
      console.log(error)
    })
}
</script>

<style lang="scss" scoped></style>
