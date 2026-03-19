<template>
  <div>
    <h2>版本管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增版本</el-button>
    <el-table :data="versions" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="版本名称" />
      <el-table-column prop="project_manager" label="项目经理" />
      <el-table-column prop="software_manager" label="软件经理" />
      <el-table-column prop="test_manager" label="测试经理" />
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="editVersion(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteVersion(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑版本' : '新增版本'">
      <el-form :model="form" label-width="100px">
        <el-form-item label="版本名称" required>
          <el-input v-model="form.name" placeholder="请输入版本名称" />
        </el-form-item>
        <el-form-item label="项目经理">
          <PersonSelect v-model="form.project_manager" placeholder="选择项目经理" />
        </el-form-item>
        <el-form-item label="软件经理">
          <PersonSelect v-model="form.software_manager" placeholder="选择软件经理" />
        </el-form-item>
        <el-form-item label="测试经理">
          <PersonSelect v-model="form.test_manager" placeholder="选择测试经理" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveVersion">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import PersonSelect from '@/components/PersonSelect.vue'

const versions = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)

const form = ref({
  id: '',
  name: '',
  project_manager: '',
  software_manager: '',
  test_manager: ''
})

const loadVersions = async () => {
  const res = await axios.get('/api/v1/versions')
  versions.value = res.data
}

const editVersion = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    project_manager: row.project_manager || '',
    software_manager: row.software_manager || '',
    test_manager: row.test_manager || ''
  }
  showAddDialog.value = true
}

const saveVersion = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入版本名称')
    return
  }
  
  try {
    const data = {
      name: form.value.name,
      project_manager: form.value.project_manager || null,
      software_manager: form.value.software_manager || null,
      test_manager: form.value.test_manager || null
    }
    
    if (isEdit.value) {
      await axios.put(`/api/v1/versions/${form.value.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/versions', data)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadVersions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const deleteVersion = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除版本 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/versions/${row.id}`)
    ElMessage.success('删除成功')
    loadVersions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadVersions()
})
</script>
