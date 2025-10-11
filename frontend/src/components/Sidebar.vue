<template>
    <div class="sidebar">
        <ul>
            <li><router-link to="/dashboard" class="sidebar-link">Dashboard</router-link></li>
            <li><router-link to="/dashboard" class="sidebar-link">Dashboard</router-link></li>
        </ul>
    </div>
</template>

<style lang="scss" scoped>
.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 200px;
    height: 100vh;
    background-color: #f2f2f2;
    padding: 20px;
}
</style>