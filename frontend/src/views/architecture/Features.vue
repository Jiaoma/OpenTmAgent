<template>
  <div>
    <h2>功能管理</h2>
    <el-button type="primary" @click="showDialog = true">新增功能</el-button>
    <el-button @click="exportMermaid">导出Mermaid</el-button>
    <el-table :data="features" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="功能名称" />
      <el-table-column label="父功能">
        <template #default="scope">
          {{ getParentName(scope.row.parent_id) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteFeature(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增功能">
      <el-form :model="form" label-width="80px">
        <el-form-item label="功能名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父功能">
          <el-select v-model="form.parent_id" placeholder="请选择" clearable>
            <el-option v-for="f in features" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="依赖模块">
          <el-select v-model="form.dependent_module_ids" multiple placeholder="请选择">
            <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createFeature">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const features = ref([])
const modules = ref([])
const showDialog = ref(false)
const form = ref({ name: '', parent_id: '', dependent_module_ids: [] })

const loadFeatures = async () => {
  const res = await axios.get('/api/v1/features')
  features.value = res.data
}

const loadModules = async () => {
  const res = await axios.get('/api/v1/modules')
  modules.value = res.data
}

const getParentName = (id) => {
  if (!id) return '-'
  const parent = features.value.find(f => f.id === id)
  return parent ? parent.name : '-'
}

const createFeature = async () => {
  try {
    await axios.post('/api/v1/features', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadFeatures()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deleteFeature = async (row) => {
  try {
    await axios.delete(`/api/v1/features/${row.id}`)
    ElMessage.success('删除成功')
    loadFeatures()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

const exportMermaid = async () => {
  const res = await axios.get('/api/v1/features/mermaid')
  navigator.clipboard.writeText(res.data.mermaid_code)
  ElMessage.success('已复制到剪贴板')
}

onMounted(() => {
  loadFeatures()
  loadModules()
})
</script>
