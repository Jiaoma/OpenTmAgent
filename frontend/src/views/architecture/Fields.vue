<template>
  <div>
    <h2>责任田管理</h2>
    <el-button type="primary" @click="showDialog = true">新增责任田</el-button>
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
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteField(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增责任田">
      <el-form :model="form" label-width="80px">
        <el-form-item label="责任田名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="所属小组">
          <el-select v-model="form.group_id" placeholder="请选择" clearable>
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="田主">
          <el-select v-model="form.owner_id" placeholder="请选择" clearable>
            <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="后备田主">
          <el-select v-model="form.backup_owner_id" placeholder="请选择" clearable>
            <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联功能">
          <el-select v-model="form.feature_ids" multiple placeholder="请选择">
            <el-option v-for="f in features" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const fields = ref([])
const groups = ref([])
const persons = ref([])
const features = ref([])
const showDialog = ref(false)
const form = ref({
  name: '',
  group_id: '',
  owner_id: '',
  backup_owner_id: '',
  feature_ids: []
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

const createField = async () => {
  try {
    await axios.post('/api/v1/responsibility-fields', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadFields()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deleteField = async (row) => {
  try {
    await axios.delete(`/api/v1/responsibility-fields/${row.id}`)
    ElMessage.success('删除成功')
    loadFields()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadFields()
  loadGroups()
  loadPersons()
  loadFeatures()
})
</script>
