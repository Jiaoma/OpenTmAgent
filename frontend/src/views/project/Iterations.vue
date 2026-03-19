<template>
  <div>
    <h2>迭代管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增迭代</el-button>
    <el-table :data="iterations" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="迭代名称" />
      <el-table-column prop="start_date" label="起始时间" />
      <el-table-column prop="end_date" label="终止时间" />
      <el-table-column prop="total_man_month" label="人月" />
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="editIteration(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteIteration(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑迭代' : '新增迭代'">
      <el-form :model="form" label-width="100px">
        <el-form-item label="所属版本">
          <el-select v-model="form.version_id" placeholder="请选择">
            <el-option v-for="v in versions" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代名称" required>
          <el-input v-model="form.name" placeholder="请输入迭代名称" />
        </el-form-item>
        <el-form-item label="起始时间" required>
          <el-date-picker v-model="form.start_date" type="date" placeholder="选择起始时间" />
        </el-form-item>
        <el-form-item label="终止时间" required>
          <el-date-picker v-model="form.end_date" type="date" placeholder="选择终止时间" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveIteration">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const iterations = ref([])
const versions = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const form = ref({
  id: '',
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

const editIteration = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    version_id: row.version_id,
    name: row.name,
    start_date: row.start_date,
    end_date: row.end_date
  }
  showAddDialog.value = true
}

const saveIteration = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入迭代名称')
    return
  }
  
  if (!form.value.start_date || !form.value.end_date) {
    ElMessage.warning('请选择起始时间和终止时间')
    return
  }
  
  try {
    const data = {
      version_id: form.value.version_id,
      name: form.value.name,
      start_date: form.value.start_date ? new Date(form.value.start_date).toISOString().split('T')[0] : '',
      end_date: form.value.end_date ? new Date(form.value.end_date).toISOString().split('T')[0] : ''
    }
    
    if (isEdit.value) {
      await axios.put(`/api/v1/iterations/${form.value.id}`, {
        name: data.name,
        start_date: data.start_date,
        end_date: data.end_date
      })
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/iterations', data)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadIterations()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const deleteIteration = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除迭代 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/iterations/${row.id}`)
    ElMessage.success('删除成功')
    loadIterations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadIterations()
  loadVersions()
})
</script>
