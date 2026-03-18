<template>
  <div>
    <h2>版本管理</h2>
    <el-button type="primary" @click="showDialog = true">新增版本</el-button>
    <el-table :data="versions" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="版本名称" />
      <el-table-column prop="project_manager" label="项目经理" />
      <el-table-column prop="software_manager" label="软件经理" />
      <el-table-column prop="test_manager" label="测试经理" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteVersion(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增版本">
      <el-form :model="form" label-width="100px">
        <el-form-item label="版本名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="项目经理">
          <el-input v-model="form.project_manager" />
        </el-form-item>
        <el-form-item label="软件经理">
          <el-input v-model="form.software_manager" />
        </el-form-item>
        <el-form-item label="测试经理">
          <el-input v-model="form.test_manager" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createVersion">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const versions = ref([])
const showDialog = ref(false)
const form = ref({
  name: '',
  project_manager: '',
  software_manager: '',
  test_manager: ''
})

const loadVersions = async () => {
  const res = await axios.get('/api/v1/versions')
  versions.value = res.data
}

const createVersion = async () => {
  try {
    await axios.post('/api/v1/versions', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadVersions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deleteVersion = async (row) => {
  try {
    await axios.delete(`/api/v1/versions/${row.id}`)
    ElMessage.success('删除成功')
    loadVersions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadVersions()
})
</script>
