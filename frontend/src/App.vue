<template>
  <el-container class="app-container">
    <el-header v-if="route.path !== '/'" class="app-header">
      <div class="header-content">
        <h1>ClickHouse Migration Tool</h1>
        <el-menu
          :default-active="activeRoute"
          mode="horizontal"
          :ellipsis="false"
          router
        >
          <el-menu-item index="/">
            <el-icon><Search /></el-icon>
            <span>Query</span>
          </el-menu-item>
          <el-menu-item index="/migration">
            <el-icon><Upload /></el-icon>
            <span>Migration</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Clock /></el-icon>
            <span>History</span>
          </el-menu-item>
          <el-menu-item index="/s3-explorer">
            <el-icon><FolderOpened /></el-icon>
            <span>S3 Explorer</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { Search, Upload, Clock, FolderOpened } from "@element-plus/icons-vue";

const route = useRoute();
const activeRoute = computed(() => route.path);
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  margin-right: 40px;
  font-size: 20px;
  color: #303133;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
}

:deep(.el-menu--horizontal) {
  border-bottom: none;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style>
