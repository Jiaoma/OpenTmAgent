<template>
  <div>
    <h2>责任田管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增责任田</el-button>
    <el-table :data="fields" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="责任田名称" />
      <el-table-column label="所属小组">
        <template #default="scope">
          {{ getGroupName(scope.row.group_id) }}
        </template>
      </el-table-column>
      <el-table-column label="田主">
        <template #default="scope">
          {{ getPersonName(scope.row.owner_id) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="scope">
          <el-button size="small" @click="editField(scope.row)">编辑</el-button>
          <el-button size="small" @click="manageFeatures(scope.row)">功能管理</el-button>
          <el-button size="small" type="danger" @click="deleteField(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑责任田' : '新增责任田'">
      <el-form :model="form" label-width="80px">
        <el-form-item label="责任田名称" required>
          <el-input v-model="form.name" placeholder="请输入责任田名称" />
        </el-form-item>
        <el-form-item label="所属小组">
          <el-select v-model="form.group_id" placeholder="请选择" clearable>
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="田主">
          <PersonSelect v-model="form.owner_id" placeholder="选择田主" />
        </el-form-item>
        <el-form-item label="后备田主">
          <PersonSelect v-model="form.backup_owner_id" placeholder="选择后备田主" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveField">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="showFeaturesDialog" title="功能关联管理" width="600px">
      <div style="margin-bottom: 16px;">
        <FeatureSelect 
          v-model="newFeatureIds" 
          :multiple="true" 
          placeholder="选择要关联的功能"
          style="width: 400px; margin-right: 8px;"
        />
        <el-button type="primary" @click="addFeatures">添加关联</el-button>
      </div>
      
      <el-table :data="fieldFeatures" style="width: 100%;">
        <el-table-column prop="name" label="功能名称" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="danger" @click="removeFeature(scope.row)">移除</el-button>
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
import PersonSelect from '@/components/PersonSelect.vue'
import FeatureSelect from '@/components/FeatureSelect.vue'

const fields = ref([])
const groups = ref([])
const persons = ref([])
const features = ref([])
const showAddDialog = ref(false)
const showFeaturesDialog = ref(false)
const isEdit = ref(false)
const currentField = ref(null)
const fieldFeatures = ref([])
const newFeatureIds = ref([])

const form = ref({
  id: '',
  name: '',
  group_id: '',
  owner_id: '',
  backup_owner_id: ''
})

const loadFields = async () => {
  const res = await axios.get('/api/v1/responsibility-fields')
  fields.value = res.data
}

const loadGroups = async () => {
  const res = await axios.get('/api/v1/groups')
  groups.value = res.data
}

const loadPersons = async () => {
  const res = await axios.get('/api/v1/persons')
  persons.value = res.data
}

const loadFeatures = async () => {
  const res = await axios.get('/api/v1/features')
  features.value = res.data
}

const getGroupName = (id) => {
  if (!id) return '-'
  const group = groups.value.find(g => g.id === id)
  return group ? group.name : '-'
}

const getPersonName = (id) => {
  if (!id) return '-'
  const person = persons.value.find(p => p.id === id)
  return person ? person.name : '-'
}

const editField = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    group_id: row.group_id || '',
    owner_id: row.owner_id || '',
    backup_owner_id: row.backup_owner_id || ''
  }
  showAddDialog.value = true
}

const saveField = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入责任田名称')
    return
  }
  
  try {
    const data = {
      name: form.value.name,
      group_id: form.value.group_id || null,
      owner_id: form.value.owner_id || null,
      backup_owner_id: form.value.backup_owner_id || null
    }
    
    if (isEdit.value) {
      await axios.put(`/api/v1/responsibility-fields/${form.value.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/responsibility-fields', {
        ...data,
        feature_ids: []
      })
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadFields()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const manageFeatures = async (row) => {
  currentField.value = row
  
  const res = await axios.get(`/api/v1/responsibility-fields/${row.id}`)
  const featureIds = res.data.features || []
  fieldFeatures.value = features.value.filter(f => featureIds.includes(f.id))
  
  newFeatureIds.value = []
  showFeaturesDialog.value = true
}

const addFeatures = async () => {
  if (!newFeatureIds.value || newFeatureIds.value.length === 0) {
    ElMessage.warning('请选择要关联的功能')
    return
  }
  
  try {
    await axios.post(`/api/v1/responsibility-fields/${currentField.value.id}/features`, {
      feature_ids: newFeatureIds.value
    })
    ElMessage.success('添加成功')
    manageFeatures(currentField.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  }
}

const removeFeature = async (feature) => {
  try {
    await ElMessageBox.confirm(`确定要移除功能 "${feature.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/responsibility-fields/${currentField.value.id}/features/${feature.id}`)
    ElMessage.success('移除成功')
    manageFeatures(currentField.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '移除失败')
    }
  }
}

const deleteField = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除责任田 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/responsibility-fields/${row.id}`)
    ElMessage.success('删除成功')
    loadFields()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadFields()
  loadGroups()
  loadPersons()
  loadFeatures()
})
</script>
