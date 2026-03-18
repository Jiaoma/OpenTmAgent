<template>
  <div>
    <h2>迭代管理</h2>
    <el-button type="primary" @click="showDialog = true">新增迭代</el-button>
    <el-table :data="iterations" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="迭代名称" />
      <el-table-column prop="start_date" label="起始时间" />
      <el-table-column prop="end_date" label="终止时间" />
      <el-table-column prop="total_man_month" label="人月" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteIteration(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增迭代">
      <el-form :model="form" label-width="100px">
        <el-form-item label="所属版本">
          <el-select v-model="form.version_id" placeholder="请选择">
            <el-option v-for="v in versions" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="起始时间">
          <el-date-picker v-model="form.start_date" type="date" />
        </el-form-item>
        <el-form-item label="终止时间">
          <el-date-picker v-model="form.end_date" type="date" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createIteration">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const iterations = ref([])
const versions = ref([])
const showDialog = ref(false)
const form = ref({
  version_id: '',
  name: '',
  start_date: '',
  end_date: ''
})

const loadIterations = async () => {
  const res = await axios.get('/api/v1/iterations')
  iterations.value = res.data
}

const loadVersions = async () => {
  const res = await axios.get('/api/v1/versions')
  versions.value = res.data
}

const createIteration = async () => {
  try {
    await axios.post('/api/v1/iterations', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadIterations()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deleteIteration = async (row) => {
  try {
    await axios.delete(`/api/v1/iterations/${row.id}`)
    ElMessage.success('删除成功')
    loadIterations()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadIterations()
  loadVersions()
})
</script>
