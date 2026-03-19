<template>
  <div>
    <h2>功能管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增功能</el-button>
    <el-button @click="exportMermaid">导出Mermaid</el-button>
    <el-table :data="features" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="功能名称" />
      <el-table-column label="父功能">
        <template #default="scope">
          {{ getParentName(scope.row.parent_id) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="scope">
          <el-button size="small" @click="editFeature(scope.row)">编辑</el-button>
          <el-button size="small" @click="manageModules(scope.row)">模块管理</el-button>
          <el-button size="small" type="danger" @click="deleteFeature(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑功能' : '新增功能'">
      <el-form :model="form" label-width="80px">
        <el-form-item label="功能名称" required>
          <el-input v-model="form.name" placeholder="请输入功能名称" />
        </el-form-item>
        <el-form-item label="父功能">
          <FeatureSelect v-model="form.parent_id" placeholder="选择父功能" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveFeature">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="showModulesDialog" title="模块关联管理" width="600px">
      <div style="margin-bottom: 16px;">
        <ModuleTreeSelect 
          v-model="newModuleIds" 
          :multiple="true" 
          placeholder="选择要关联的模块"
          style="width: 400px; margin-right: 8px;"
        />
        <el-button type="primary" @click="addModules">添加关联</el-button>
      </div>
      
      <el-table :data="featureModules" style="width: 100%;">
        <el-table-column prop="name" label="模块名称" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="danger" @click="removeModule(scope.row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import FeatureSelect from '@/components/FeatureSelect.vue'
import ModuleTreeSelect from '@/components/ModuleTreeSelect.vue'

const features = ref([])
const modules = ref([])
const showAddDialog = ref(false)
const showModulesDialog = ref(false)
const isEdit = ref(false)
const currentFeature = ref(null)
const featureModules = ref([])
const newModuleIds = ref([])

const form = ref({
  id: '',
  name: '',
  parent_id: ''
})

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

const editFeature = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    parent_id: row.parent_id || ''
  }
  showAddDialog.value = true
}

const saveFeature = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入功能名称')
    return
  }
  
  try {
    const data = {
      name: form.value.name,
      parent_id: form.value.parent_id || null
    }
    
    if (isEdit.value) {
      await axios.put(`/api/v1/features/${form.value.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/features', {
        ...data,
        dependent_module_ids: []
      })
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadFeatures()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const manageModules = async (row) => {
  currentFeature.value = row
  
  const res = await axios.get(`/api/v1/features/${row.id}`)
  const moduleIds = res.data.dependent_modules || []
  featureModules.value = modules.value.filter(m => moduleIds.includes(m.id))
  
  newModuleIds.value = []
  showModulesDialog.value = true
}

const addModules = async () => {
  if (!newModuleIds.value || newModuleIds.value.length === 0) {
    ElMessage.warning('请选择要关联的模块')
    return
  }
  
  try {
    await axios.post(`/api/v1/features/${currentFeature.value.id}/modules`, {
      module_ids: newModuleIds.value
    })
    ElMessage.success('添加成功')
    manageModules(currentFeature.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  }
}

const removeModule = async (module) => {
  try {
    await ElMessageBox.confirm(`确定要移除模块 "${module.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/features/${currentFeature.value.id}/modules/${module.id}`)
    ElMessage.success('移除成功')
    manageModules(currentFeature.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '移除失败')
    }
  }
}

const deleteFeature = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除功能 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/features/${row.id}`)
    ElMessage.success('删除成功')
    loadFeatures()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
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
