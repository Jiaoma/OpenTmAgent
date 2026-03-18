<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background-color: #545c64">
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-sub-menu index="team">
          <template #title>
            <el-icon><User /></el-icon>
            <span>团队管理</span>
          </template>
          <el-menu-item index="/team/persons">人员管理</el-menu-item>
          <el-menu-item index="/team/groups">小组管理</el-menu-item>
          <el-menu-item index="/team/ability">能力模型</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="project">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>项目管理</span>
          </template>
          <el-menu-item index="/project/versions">版本管理</el-menu-item>
          <el-menu-item index="/project/iterations">迭代管理</el-menu-item>
          <el-menu-item index="/project/tasks">任务管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="architecture">
          <template #title>
            <el-icon><Grid /></el-icon>
            <span>架构档案</span>
          </template>
          <el-menu-item index="/architecture/modules">模块管理</el-menu-item>
          <el-menu-item index="/architecture/features">功能管理</el-menu-item>
          <el-menu-item index="/architecture/fields">责任田</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background-color: #fff; border-bottom: 1px solid #eee">
        <div style="display: flex; justify-content: space-between; align-items: center; height: 100%">
          <h2 style="margin: 0">OpenTmAgent</h2>
          <div>
            <span v-if="user">{{ user.employee_id }}</span>
            <el-button v-if="!user" type="primary" @click="$router.push('/login')">登录</el-button>
            <el-button v-else type="danger" @click="logout">登出</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, User, Document, Grid } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const user = ref(null)

const activeMenu = computed(() => route.path)

const logout = () => {
  user.value = null
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
</style>
