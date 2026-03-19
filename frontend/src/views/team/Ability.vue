<template>
  <div>
    <h2>能力模型管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增能力维度</el-button>
    <el-table :data="dimensions" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="维度名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="editDimension(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteDimension(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑能力维度' : '新增能力维度'">
      <el-form :model="form" label-width="100px">
        <el-form-item label="维度名称" required>
          <el-input v-model="form.name" placeholder="请输入维度名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="等级1描述">
          <el-input v-model="form.level_1_desc" placeholder="请输入等级1描述" />
        </el-form-item>
        <el-form-item label="等级2描述">
          <el-input v-model="form.level_2_desc" placeholder="请输入等级2描述" />
        </el-form-item>
        <el-form-item label="等级3描述">
          <el-input v-model="form.level_3_desc" placeholder="请输入等级3描述" />
        </el-form-item>
        <el-form-item label="等级4描述">
          <el-input v-model="form.level_4_desc" placeholder="请输入等级4描述" />
        </el-form-item>
        <el-form-item label="等级5描述">
          <el-input v-model="form.level_5_desc" placeholder="请输入等级5描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDimension">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const dimensions = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const form = ref({
  id: '',
  name: '',
  description: '',
  level_1_desc: '',
  level_2_desc: '',
  level_3_desc: '',
  level_4_desc: '',
  level_5_desc: ''
})

const loadDimensions = async () => {
  const res = await axios.get('/api/v1/ability-dimensions')
  dimensions.value = res.data
}

const editDimension = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    description: row.description || '',
    level_1_desc: row.level_1_desc || '',
    level_2_desc: row.level_2_desc || '',
    level_3_desc: row.level_3_desc || '',
    level_4_desc: row.level_4_desc || '',
    level_5_desc: row.level_5_desc || ''
  }
  showAddDialog.value = true
}

const saveDimension = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入维度名称')
    return
  }
  
  try {
    const data = {
      name: form.value.name,
      description: form.value.description || null,
      level_1_desc: form.value.level_1_desc || null,
      level_2_desc: form.value.level_2_desc || null,
      level_3_desc: form.value.level_3_desc || null,
      level_4_desc: form.value.level_4_desc || null,
      level_5_desc: form.value.level_5_desc || null
    }
    
    if (isEdit.value) {
      await axios.put(`/api/v1/ability-dimensions/${form.value.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/ability-dimensions', data)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadDimensions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const deleteDimension = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除能力维度 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/ability-dimensions/${row.id}`)
    ElMessage.success('删除成功')
    loadDimensions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadDimensions()
})
</script>
