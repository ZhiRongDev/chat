<template>
    <Sidebar></Sidebar>
    <div class="content">
        <router-view></router-view>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/Sidebar.vue';
</script>


<style lang="scss" scoped>
.content {
    padding-left: 200px;
}
</style>