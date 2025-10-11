<template>
  <form action="" class="form" @submit.prevent="register">
    <div class="mb-3">
      <label for="username" class="form-label">Email</label>
      <input type="email" class="form-control" id="username" placeholder="Email" v-model="username" />
    </div>
    <div class="mb-3">
      <label for="password" class="form-label">Password</label>
      <input type="password" class="form-control" id="password" placeholder="Password" v-model="password" />
    </div>
    <button type="submit" class="btn btn-primary w-100 mb-3">Register</button>
    <router-link to="/login">Back to login</router-link>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api/service'
import { appendAlert } from '@/utils/alert'
import { useRouter } from 'vue-router'

const router = useRouter()


const username = ref('')
const password = ref('')

const register = () => {
  api
    .post('/user', {
      username: username.value,
      password: password.value
    })
    .then((response) => {
      appendAlert('Register success', 'success')
      router.push('/login')
    })
    .catch((error) => {
      console.error(error)
      appendAlert(error.response.data.detail, 'danger')
    })
}
</script>

<style lang="scss" scoped></style>
