<template>
  <el-container class="main-layout">
    <el-header class="app-header">
      <div class="header-content">
        <h1>ClickHouse Migration Tool</h1>
        <el-menu
          :default-active="activeRoute"
          mode="horizontal"
          :ellipsis="false"
          router
        >
          <el-menu-item index="/query">
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
        <div class="user-menu">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ userName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Search,
  Upload,
  Clock,
  FolderOpened,
  User,
  SwitchButton,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { authApi } from "@/api";

const route = useRoute();
const router = useRouter();
const activeRoute = computed(() => route.path);
const userName = ref("User");

onMounted(() => {
  const userStr = localStorage.getItem("user");
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      userName.value = user.name || user.username || user.email || "User";
    } catch (e) {
      console.error("Error parsing user data:", e);
    }
  }
});

const handleCommand = async (command: string) => {
  if (command === "logout") {
    try {
      await ElMessageBox.confirm(
        "Are you sure you want to logout?",
        "Confirm Logout",
        {
          confirmButtonText: "Logout",
          cancelButtonText: "Cancel",
          type: "warning",
        }
      );

      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          await authApi.logout(refreshToken);
        } catch (e) {
          console.error("Logout API error:", e);
        }
      }

      // Clear localStorage
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");

      ElMessage.success("Logged out successfully");
      router.push("/");
    } catch (e) {
      // User cancelled
    }
  }
};
</script>

<style scoped>
.main-layout {
  height: 100vh;
  width: 100%;
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

.user-menu {
  margin-left: auto;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

:deep(.el-menu--horizontal) {
  border-bottom: none;
}
</style>
