<template>
  <div style="display: flex; justify-content: center; align-items: center; height: 100%">
    <el-card style="width: 400px">
      <h2 style="text-align: center">登录</h2>
      <el-tabs v-model="loginType">
        <el-tab-pane label="管理员登录" name="admin">
          <el-form :model="adminForm" label-width="80px">
            <el-form-item label="工号">
              <el-input v-model="adminForm.employee_id" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="adminForm.password" type="password" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="adminLogin">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="访客登录" name="visitor">
          <el-form :model="visitorForm" label-width="80px">
            <el-form-item label="工号">
              <el-input v-model="visitorForm.employee_id" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="visitorLogin">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const loginType = ref('admin')
const adminForm = ref({ employee_id: '', password: '' })
const visitorForm = ref({ employee_id: '' })

const adminLogin = async () => {
  try {
    const res = await axios.post('/api/v1/auth/admin-login', adminForm.value)
    if (res.data.success) {
      localStorage.setItem('token', res.data.token.access_token)
      ElMessage.success('登录成功')
      router.push('/')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  }
}

const visitorLogin = async () => {
  try {
    const res = await axios.post('/api/v1/auth/visitor-login', visitorForm.value)
    if (res.data.success) {
      localStorage.setItem('token', res.data.token.access_token)
      ElMessage.success('登录成功')
      router.push('/')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  }
}
</script>
