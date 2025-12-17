<template>
  <div class="login-container">
    <div class="login-content">
      <div class="logo-wrapper">
        <img src="/logo_banksultra_blue.png" alt="Logo" class="login-logo" />
      </div>
      <el-card class="login-card">
        <el-tabs v-model="activeTab" stretch>
          <el-tab-pane label="Login" name="login">
            <div class="tab-content">
              <div class="card-header">
                <h2 class="card-title">Welcome back</h2>
                <p class="card-desc">
                  Enter your credentials to access your account
                </p>
              </div>
              <el-form @submit.prevent="handleLogin" class="login-form">
                <el-form-item>
                  <el-input
                    v-model="username"
                    placeholder="Username or Email"
                    :prefix-icon="Mail"
                    autocomplete="username"
                    size="large"
                  />
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Password"
                    :prefix-icon="Lock"
                    autocomplete="current-password"
                    size="large"
                    :suffix-icon="showPassword ? EyeOff : Eye"
                    @suffix-icon-click="toggleShowPassword"
                  >
                    <template #suffix>
                      <el-icon @click="toggleShowPassword" class="password-eye">
                        <component :is="showPassword ? EyeOff : Eye" />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <div class="form-row form-remember">
                  <el-checkbox v-model="rememberMe"
                    >Remember me for 30 days</el-checkbox
                  >
                  <router-link to="/forgot-password" class="forgot-link"
                    >Forgot password?</router-link
                  >
                </div>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleLogin"
                    class="login-btn"
                    :loading="loading"
                    size="large"
                    block
                  >
                    <el-icon><LogIn /></el-icon>
                    <span v-if="!loading">Login</span>
                    <span v-else>Logging in...</span>
                  </el-button>
                </el-form-item>
              </el-form>
              <div class="divider">Or continue with</div>
              <div class="social-row">
                <el-button plain class="social-btn" size="large" block>
                  <el-icon><Github /></el-icon> Github
                </el-button>
                <el-button plain class="social-btn" size="large" block>
                  <el-icon><Twitter /></el-icon> Twitter
                </el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="Sign Up" name="signup">
            <div class="tab-content">
              <div class="card-header">
                <h2 class="card-title">Create an account</h2>
                <p class="card-desc">
                  Sign up is currently disabled. Please contact administrator.
                </p>
              </div>
              <el-form class="login-form">
                <el-form-item>
                  <el-input
                    placeholder="Full Name"
                    :prefix-icon="User"
                    size="large"
                    disabled
                  />
                </el-form-item>
                <el-form-item>
                  <el-input
                    placeholder="Email"
                    :prefix-icon="Mail"
                    size="large"
                    disabled
                  />
                </el-form-item>
                <el-form-item>
                  <el-input
                    placeholder="Password"
                    :prefix-icon="Lock"
                    size="large"
                    disabled
                  />
                </el-form-item>
                <el-form-item>
                  <el-checkbox disabled
                    >I agree to the Terms of Service and Privacy
                    Policy</el-checkbox
                  >
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" size="large" block disabled>
                    <el-icon><ArrowRight /></el-icon>
                    Create Account
                  </el-button>
                </el-form-item>
              </el-form>
              <div class="divider">Or continue with</div>
              <div class="social-row">
                <el-button plain class="social-btn" size="large" block>
                  <el-icon><Github /></el-icon> Github
                </el-button>
                <el-button plain class="social-btn" size="large" block>
                  <el-icon><Twitter /></el-icon> Twitter
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        <div class="footer-info">
          <span>
            By continuing, you acknowledge that you have read and understood our
            <router-link to="/terms" class="footer-link"
              >Terms of Service</router-link
            >
            and
            <router-link to="/privacy" class="footer-link"
              >Privacy Policy</router-link
            >
          </span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  LogIn,
  ArrowRight,
  Github,
  Twitter,
} from "@element-plus/icons-vue";

const username = ref("");
const password = ref("");
const showPassword = ref(false);
const rememberMe = ref(false);
const loading = ref(false);
const activeTab = ref("login");
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
  setTimeout(() => {
    loading.value = false;
    router.push("/query");
  }, 1000);
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to bottom, #f5f7fa, #e9ecef 80%);
}
.login-content {
  width: 100%;
  max-width: 420px;
  animation: fade-in 0.7s;
}
.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}
.login-logo {
  height: 40px;
  width: auto;
}
.login-card {
  box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.08);
  border-top: 4px solid #409eff;
  padding: 0 0 10px 0;
}
.card-header {
  text-align: center;
  margin-bottom: 18px;
}
.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 2px;
}
.card-desc {
  color: #909399;
  font-size: 1rem;
}
.login-form {
  margin-top: 10px;
}
.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.form-remember {
  margin-bottom: 10px;
}
.forgot-link {
  font-size: 13px;
  color: #409eff;
  text-decoration: none;
}
.forgot-link:hover {
  text-decoration: underline;
}
.login-btn {
  width: 100%;
  font-weight: 500;
  margin-top: 8px;
}
.divider {
  position: relative;
  text-align: center;
  margin: 24px 0 16px 0;
  color: #bfc2c7;
  font-size: 13px;
}
.divider:before,
.divider:after {
  content: "";
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #e4e7ed;
}
.divider:before {
  left: 0;
}
.divider:after {
  right: 0;
}
.social-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}
.social-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.password-eye {
  cursor: pointer;
}
.footer-info {
  margin-top: 18px;
  text-align: center;
  font-size: 13px;
  color: #909399;
  padding: 0 10px 8px 10px;
}
.footer-link {
  color: #409eff;
  margin: 0 2px;
  text-decoration: none;
}
.footer-link:hover {
  text-decoration: underline;
}
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
