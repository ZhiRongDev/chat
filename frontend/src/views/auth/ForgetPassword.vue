<template>
  <form action="" class="form" @submit.prevent="">
    <div class="mb-3">
      <label for="username" class="form-label">Email</label>
      <input type="email" class="form-control" id="username" placeholder="Email" />
    </div>
    <button type="submit" class="btn btn-primary w-100 mb-3">Send</button>
    <router-link to="/login">Back to login</router-link>
  </form>
</template>

<script setup lang="ts"></script>

<style lang="scss" scoped></style>
