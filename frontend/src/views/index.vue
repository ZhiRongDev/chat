<template>
  <div class="wrapper">
    <div class="d-flex flex-column align-items-center">
      <h1 class="logo mb-3">Chat App</h1>
      <form action="" class="form" @submit.prevent="login">
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
        <button type="submit" class="btn btn-primary">login</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const username = ref('');
const password = ref('');


const login = () => {
  console.log('login', username.value, password.value);
}

// import * as bootstrap from 'bootstrap'
// function openModal() {
//   const exampleModal = new bootstrap.Modal('#exampleModal')
//   exampleModal.show()
// }
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.logo {
  display: block;
  width: 150px;
  height: 150px;
  background-image: url('@/assets/img/logo.png');
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  white-space: nowrap;
  text-indent: 100%;
  overflow: hidden;
}
</style>

