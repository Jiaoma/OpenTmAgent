<template>
  <div>
    <h2>人员管理</h2>
    <el-button type="primary" @click="showDialog = true">新增人员</el-button>
    <el-table :data="persons" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="employee_id" label="工号" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="position" label="职位" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editPerson(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deletePerson(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增人员">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="工号">
          <el-input v-model="form.employee_id" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createPerson">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const persons = ref([])
const showDialog = ref(false)
const form = ref({ name: '', employee_id: '', email: '', position: '' })

const loadPersons = async () => {
  const res = await axios.get('/api/v1/persons')
  persons.value = res.data
}

const createPerson = async () => {
  try {
    await axios.post('/api/v1/persons', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadPersons()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deletePerson = async (row) => {
  try {
    await axios.delete(`/api/v1/persons/${row.id}`)
    ElMessage.success('删除成功')
    loadPersons()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadPersons()
})
</script>
