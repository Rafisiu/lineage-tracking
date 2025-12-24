import { createRouter, createWebHistory } from "vue-router";
import AuthLayout from "../layouts/AuthLayout.vue";
import MainLayout from "../layouts/MainLayout.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: AuthLayout,
      children: [
        {
          path: "",
          name: "login",
          component: () => import("../views/LoginView.vue"),
        },
      ],
    },
    {
      path: "/",
      component: MainLayout,
      children: [
        {
          path: "query",
          name: "query",
          component: () => import("../views/QueryView.vue"),
        },
        {
          path: "migration",
          name: "migration",
          component: () => import("../views/MigrationView.vue"),
        },
        {
          path: "history",
          name: "history",
          component: () => import("../views/HistoryView.vue"),
        },
        {
          path: "s3-explorer",
          name: "s3-explorer",
          component: () => import("../views/S3ExplorerView.vue"),
        },
      ],
    },
  ],
});

export default router;
