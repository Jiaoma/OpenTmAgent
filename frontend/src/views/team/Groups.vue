<template>
  <div>
    <h2>小组管理</h2>
    <el-button type="primary" @click="showDialog = true">新增小组</el-button>
    <el-table :data="groups" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="组名" />
      <el-table-column label="组长">
        <template #default="scope">
          {{ getPersonName(scope.row.leader_id) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="viewGroup(scope.row)">查看</el-button>
          <el-button size="small" type="danger" @click="deleteGroup(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增小组">
      <el-form :model="form" label-width="80px">
        <el-form-item label="组名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="组长">
          <el-select v-model="form.leader_id" placeholder="请选择">
            <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createGroup">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const groups = ref([])
const persons = ref([])
const showDialog = ref(false)
const form = ref({ name: '', leader_id: '', member_ids: [] })

const loadGroups = async () => {
  const res = await axios.get('/api/v1/groups')
  groups.value = res.data
}

const loadPersons = async () => {
  const res = await axios.get('/api/v1/persons')
  persons.value = res.data
}

const getPersonName = (id) => {
  const person = persons.value.find(p => p.id === id)
  return person ? person.name : '-'
}

const createGroup = async () => {
  try {
    await axios.post('/api/v1/groups', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadGroups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deleteGroup = async (row) => {
  try {
    await axios.delete(`/api/v1/groups/${row.id}`)
    ElMessage.success('删除成功')
    loadGroups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

const viewGroup = (row) => {
  // TODO: navigate to group detail
}

onMounted(() => {
  loadGroups()
  loadPersons()
})
</script>
