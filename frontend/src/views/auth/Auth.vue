<template>
  <div class="wrapper">
    <div class="d-flex flex-column align-items-center">
      <h1 class="logo mb-3">Chat App</h1>
      <router-view></router-view>
    </div>
  </div>
</template>

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
