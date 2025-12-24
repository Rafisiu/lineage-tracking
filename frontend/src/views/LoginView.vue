<template>
  <div
    style="
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(to bottom, #f5f7fa, #e9ecef 80%);
    "
  >
    <div style="width: 100%; max-width: 420px; animation: fade-in 0.7s">
      <div style="display: flex; justify-content: center; margin-bottom: 24px">
        <!-- <img src="/logo_banksultra_blue.png" alt="Logo" style="height: 40px; width: auto;" /> -->
      </div>
      <el-card
        style="
          box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.08);
          border-top: 4px solid #409eff;
          padding: 0 0 10px 0;
        "
      >
        <div style="text-align: center; margin-bottom: 18px">
          <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 2px">
            Welcome back
          </h2>
          <p style="color: #909399; font-size: 1rem">
            Enter your email and password to access your account
          </p>
        </div>
        <el-form @submit.prevent="handleLogin" style="margin-top: 10px">
          <el-form-item>
            <el-input
              v-model="username"
              placeholder="Email"
              autocomplete="username"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Password"
              autocomplete="current-password"
              size="large"
              :prefix-icon="Lock"
            >
              <template #suffix>
                <el-icon @click="toggleShowPassword" style="cursor: pointer">
                  <component :is="showPassword ? 'ViewOff' : 'View'" />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              @click="handleLogin"
              style="width: 100%; font-weight: 500; margin-top: 8px"
              :loading="loading"
              size="large"
              block
            >
              Login
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
import { authApi } from "@/api";

const username = ref("");
const password = ref("");
const showPassword = ref(false);
const loading = ref(false);
const router = useRouter();

const toggleShowPassword = () => {
  showPassword.value = !showPassword.value;
};

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning("Please enter username and password");
    return;
  }

  loading.value = true;

  try {
    const response = await authApi.login(username.value, password.value);

    if (response.data.success) {
      const { access_token, refresh_token } = response.data.data;

      // Decode JWT access_token to get preferred_username
      let user: any = {};
      try {
        const base64Url = access_token.split(".")[1];
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split("")
            .map(function (c) {
              return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
            })
            .join("")
        );
        const payload = JSON.parse(jsonPayload);
        user = {
          name: payload.preferred_username,
          ...payload,
        };
      } catch (e) {
        user = { name: "User" };
      }

      // Save tokens and user info to localStorage
      localStorage.setItem("access_token", access_token);
      if (refresh_token) {
        localStorage.setItem("refresh_token", refresh_token);
      }
      localStorage.setItem("user", JSON.stringify(user));

      ElMessage.success(
        `Welcome back, ${
          user.name || user.preferred_username || user.username || "User"
        }!`
      );

      // Redirect to query page
      router.push("/query");
    } else {
      ElMessage.error("Login failed");
    }
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.detail ||
      "Login failed. Please check your credentials.";
    ElMessage.error(errorMessage);
  } finally {
    loading.value = false;
  }
};
</script>
