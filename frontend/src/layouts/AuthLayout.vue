<template>
  <div class="auth-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// Auth layout - simple container without header
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}
</style>
