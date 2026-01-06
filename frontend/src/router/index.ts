import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomePage.vue'),
    meta: {
      title: '首页',
      keepAlive: true,
    },
  },
  {
    path: '/today',
    name: 'today',
    component: () => import('@/views/TodayPage.vue'),
    meta: {
      title: '今日精选',
      keepAlive: true,
    },
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchPage.vue'),
    meta: {
      title: '搜索',
    },
  },
  {
    path: '/categories',
    name: 'categories',
    component: () => import('@/views/CategoriesPage.vue'),
    meta: {
      title: '分类',
      keepAlive: true,
    },
  },
  {
    path: '/article/:id',
    name: 'article-detail',
    component: () => import('@/views/ArticleDetailPage.vue'),
    meta: {
      title: '文章详情',
    },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/AdminPage.vue'),
    meta: {
      title: '管理后台',
      requiresAuth: true,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginPage.vue'),
    meta: {
      title: '登录',
      guestOnly: true,
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterPage.vue'),
    meta: {
      title: '注册',
      guestOnly: true,
    },
  },
  {
    path: '/profile',
    name: 'profile',
    // We haven't created ProfilePage yet, but we will. Use admin as placeholder or create empty.
    // Let's use basic auth check for now.
    component: () => import('@/views/auth/LoginPage.vue'), // Placeholder
    meta: {
      title: '个人中心',
      requiresAuth: true,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundPage.vue'),
    meta: {
      title: '页面未找到',
    },
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// 路由守卫
import { useAuthStore } from '@/stores/auth'

router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - AI 新闻`
  } else {
    document.title = 'AI 新闻'
  }

  const authStore = useAuthStore()
  
  // 如果有 token 但用户信息未加载，尝试加载
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchCurrentUser()
  }

  // 权限检查
  if (to.meta?.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    } else {
      next()
    }
  } else if (to.meta?.guestOnly) {
    if (authStore.isAuthenticated) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
