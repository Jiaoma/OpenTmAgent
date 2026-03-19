<template>
  <div>
    <h2>模块管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增模块</el-button>
    <el-button @click="exportMermaid">导出Mermaid</el-button>
    <el-table :data="modules" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="模块名称" />
      <el-table-column label="父模块">
        <template #default="scope">
          {{ getParentName(scope.row.parent_id) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="editModule(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteModule(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑模块' : '新增模块'">
      <el-form :model="form" label-width="80px">
        <el-form-item label="模块名称" required>
          <el-input v-model="form.name" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="父模块">
          <ModuleTreeSelect v-model="form.parent_id" placeholder="选择父模块" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveModule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import ModuleTreeSelect from '@/components/ModuleTreeSelect.vue'

const modules = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const form = ref({ id: '', name: '', parent_id: '' })

const loadModules = async () => {
  const res = await axios.get('/api/v1/modules')
  modules.value = res.data
}

const getParentName = (id) => {
  if (!id) return '-'
  const parent = modules.value.find(m => m.id === id)
  return parent ? parent.name : '-'
}

const editModule = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    parent_id: row.parent_id || ''
  }
  showAddDialog.value = true
}

const saveModule = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入模块名称')
    return
  }
  
  try {
    const data = {
      name: form.value.name,
      parent_id: form.value.parent_id || null
    }
    
    if (isEdit.value) {
      await axios.put(`/api/v1/modules/${form.value.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/modules', data)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadModules()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const deleteModule = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除模块 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/modules/${row.id}`)
    ElMessage.success('删除成功')
    loadModules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const exportMermaid = async () => {
  const res = await axios.get('/api/v1/modules/mermaid')
  navigator.clipboard.writeText(res.data.mermaid_code)
  ElMessage.success('已复制到剪贴板')
}

onMounted(() => {
  loadModules()
})
</script>
