<template>
  <div>
    <h2>任务管理</h2>
    <el-button type="primary" @click="showDialog = true">新增任务</el-button>
    <el-table :data="tasks" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="start_date" label="起始时间" />
      <el-table-column prop="end_date" label="终止时间" />
      <el-table-column prop="man_month" label="人月" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="updateStatus(scope.row)">更新状态</el-button>
          <el-button size="small" type="danger" @click="deleteTask(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增任务">
      <el-form :model="form" label-width="100px">
        <el-form-item label="所属迭代">
          <el-select v-model="form.iteration_id" placeholder="请选择">
            <el-option v-for="i in iterations" :key="i.id" :label="i.name" :value="i.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="起始时间">
          <el-date-picker v-model="form.start_date" type="date" />
        </el-form-item>
        <el-form-item label="终止时间">
          <el-date-picker v-model="form.end_date" type="date" />
        </el-form-item>
        <el-form-item label="人月">
          <el-input-number v-model="form.man_month" :min="0.1" :step="0.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const tasks = ref([])
const iterations = ref([])
const showDialog = ref(false)
const form = ref({
  iteration_id: '',
  name: '',
  start_date: '',
  end_date: '',
  man_month: 1.0
})

const loadTasks = async () => {
  const res = await axios.get('/api/v1/tasks')
  tasks.value = res.data
}

const loadIterations = async () => {
  const res = await axios.get('/api/v1/iterations')
  iterations.value = res.data
}

const createTask = async () => {
  try {
    await axios.post('/api/v1/tasks', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const updateStatus = async (row) => {
  const status = row.status === 'pending' ? 'in_progress' : row.status === 'in_progress' ? 'completed' : 'pending'
  try {
    await axios.put(`/api/v1/tasks/${row.id}`, { status })
    ElMessage.success('更新成功')
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

const deleteTask = async (row) => {
  try {
    await axios.delete(`/api/v1/tasks/${row.id}`)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadTasks()
  loadIterations()
})
</script>
