<template>
  <div>
    <h2>能力模型管理</h2>
    <el-button type="primary" @click="showDialog = true">新增能力维度</el-button>
    <el-table :data="dimensions" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="维度名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteDimension(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" title="新增能力维度">
      <el-form :model="form" label-width="100px">
        <el-form-item label="维度名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="等级1描述">
          <el-input v-model="form.level_1_desc" />
        </el-form-item>
        <el-form-item label="等级2描述">
          <el-input v-model="form.level_2_desc" />
        </el-form-item>
        <el-form-item label="等级3描述">
          <el-input v-model="form.level_3_desc" />
        </el-form-item>
        <el-form-item label="等级4描述">
          <el-input v-model="form.level_4_desc" />
        </el-form-item>
        <el-form-item label="等级5描述">
          <el-input v-model="form.level_5_desc" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createDimension">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const dimensions = ref([])
const showDialog = ref(false)
const form = ref({
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

const createDimension = async () => {
  try {
    await axios.post('/api/v1/ability-dimensions', form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadDimensions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const deleteDimension = async (row) => {
  try {
    await axios.delete(`/api/v1/ability-dimensions/${row.id}`)
    ElMessage.success('删除成功')
    loadDimensions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadDimensions()
})
</script>
