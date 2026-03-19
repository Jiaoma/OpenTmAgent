<template>
  <div>
    <h2>任务管理</h2>
    <el-button type="primary" @click="openCreateDialog">新增任务</el-button>
    <el-table :data="tasks" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="start_date" label="起始时间" />
      <el-table-column prop="end_date" label="终止时间" />
      <el-table-column prop="man_month" label="人月" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" @click="updateStatus(scope.row)">更新状态</el-button>
          <el-button size="small" type="danger" @click="deleteTask(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑任务' : '新增任务'" width="700px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="所属迭代">
          <el-select v-model="form.iteration_id" placeholder="请选择" :disabled="isEdit">
            <el-option v-for="i in iterations" :key="i.id" :label="i.name" :value="i.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="起始时间">
          <el-date-picker v-model="form.start_date" type="date" />
        </el-form-item>
        <el-form-item label="终止时间">
          <el-date-picker v-model="form.end_date" type="date" />
        </el-form-item>
        <el-form-item label="人月">
          <el-input-number v-model="form.man_month" :min="0.1" :step="0.1" />
        </el-form-item>
        <el-form-item label="设计文档URL">
          <el-input v-model="form.design_doc_url" placeholder="可选" />
        </el-form-item>
        
        <el-divider content-position="left">人员配置</el-divider>
        
        <el-form-item label="特性负责人">
          <div style="display: flex; gap: 10px; width: 100%;">
            <PersonSelect
              v-model="form.feature_owner.person_id"
              placeholder="选择人员"
              style="flex: 1;"
            />
            <el-input v-model="form.feature_owner.role" placeholder="角色" style="width: 150px;" />
          </div>
        </el-form-item>
        
        <el-form-item label="开发负责人">
          <div v-for="(dev, index) in form.dev_owners" :key="index" style="display: flex; gap: 10px; margin-bottom: 10px; width: 100%;">
            <PersonSelect
              v-model="dev.person_id"
              placeholder="选择人员"
              style="flex: 1;"
            />
            <el-input v-model="dev.role" placeholder="角色" style="width: 150px;" />
            <el-button type="danger" :icon="Delete" circle @click="removeDevOwner(index)" />
          </div>
          <el-button type="primary" size="small" @click="addDevOwner">添加开发负责人</el-button>
        </el-form-item>
        
        <el-form-item label="测试人员">
          <el-select
            v-model="form.testers"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入测试人员姓名"
          >
            <el-option
              v-for="tester in form.testers"
              :key="tester"
              :label="tester"
              :value="tester"
            />
          </el-select>
        </el-form-item>
        
        <el-divider content-position="left">任务依赖</el-divider>
        
        <el-form-item label="依赖任务">
          <div v-for="(dep, index) in form.dependencies" :key="index" style="display: flex; gap: 10px; margin-bottom: 10px; width: 100%;">
            <TaskSelect
              v-model="dep.related_task_id"
              :iteration-id="form.iteration_id"
              placeholder="选择任务"
              style="flex: 1;"
            />
            <el-select v-model="dep.relation_type" placeholder="关系类型" style="width: 150px;">
              <el-option label="依赖" value="depends_on" />
              <el-option label="相关" value="related_to" />
            </el-select>
            <el-button type="danger" :icon="Delete" circle @click="removeDependency(index)" />
          </div>
          <el-button type="primary" size="small" @click="addDependency">添加依赖</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="isEdit ? updateTask() : createTask()">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import PersonSelect from '@/components/PersonSelect.vue'
import TaskSelect from '@/components/TaskSelect.vue'

const tasks = ref([])
const iterations = ref([])
const showDialog = ref(false)
const isEdit = ref(false)
const editingTaskId = ref('')

const emptyForm = () => ({
  iteration_id: '',
  name: '',
  start_date: '',
  end_date: '',
  man_month: 1.0,
  design_doc_url: '',
  feature_owner: {
    person_id: '',
    person_name: '',
    role: ''
  },
  dev_owners: [],
  testers: [],
  dependencies: []
})

const form = ref(emptyForm())

const loadTasks = async () => {
  const res = await axios.get('/api/v1/tasks')
  tasks.value = res.data
}

const loadIterations = async () => {
  const res = await axios.get('/api/v1/iterations')
  iterations.value = res.data
}

const loadTaskDetail = async (taskId) => {
  const res = await axios.get(`/api/v1/tasks/${taskId}`)
  return res.data
}

const openCreateDialog = () => {
  isEdit.value = false
  editingTaskId.value = ''
  form.value = emptyForm()
  showDialog.value = true
}

const openEditDialog = async (row) => {
  isEdit.value = true
  editingTaskId.value = row.id
  try {
    const detail = await loadTaskDetail(row.id)
    form.value = {
      iteration_id: detail.iteration_id,
      name: detail.name,
      start_date: detail.start_date,
      end_date: detail.end_date,
      man_month: detail.man_month,
      design_doc_url: detail.design_doc_url || '',
      feature_owner: detail.feature_owner || { person_id: '', person_name: '', role: '' },
      dev_owners: detail.dev_owners || [],
      testers: detail.testers || [],
      dependencies: detail.dependencies || []
    }
    showDialog.value = true
  } catch (error) {
    ElMessage.error('加载任务详情失败')
  }
}

const addDevOwner = () => {
  form.value.dev_owners.push({
    person_id: '',
    person_name: '',
    role: ''
  })
}

const removeDevOwner = (index) => {
  form.value.dev_owners.splice(index, 1)
}

const addDependency = () => {
  form.value.dependencies.push({
    related_task_id: '',
    relation_type: 'depends_on'
  })
}

const removeDependency = (index) => {
  form.value.dependencies.splice(index, 1)
}

const createTask = async () => {
  try {
    const data = {
      ...form.value,
      start_date: form.value.start_date ? new Date(form.value.start_date).toISOString().split('T')[0] : '',
      end_date: form.value.end_date ? new Date(form.value.end_date).toISOString().split('T')[0] : '',
      feature_owner: form.value.feature_owner.person_id ? form.value.feature_owner : null,
      dev_owners: form.value.dev_owners.filter(d => d.person_id),
      dependencies: form.value.dependencies.filter(d => d.related_task_id)
    }
    await axios.post('/api/v1/tasks', data)
    ElMessage.success('创建成功')
    showDialog.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  }
}

const updateTask = async () => {
  try {
    const data = {
      name: form.value.name,
      start_date: form.value.start_date ? new Date(form.value.start_date).toISOString().split('T')[0] : null,
      end_date: form.value.end_date ? new Date(form.value.end_date).toISOString().split('T')[0] : null,
      man_month: form.value.man_month,
      design_doc_url: form.value.design_doc_url || null
    }
    await axios.put(`/api/v1/tasks/${editingTaskId.value}`, data)
    ElMessage.success('更新成功')
    showDialog.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

const updateStatus = async (row) => {
  const status = row.status === 'pending' ? 'in_progress' : row.status === 'in_progress' ? 'completed' : 'pending'
  try {
    await axios.put(`/api/v1/tasks/${row.id}`, { status })
    ElMessage.success('更新成功')
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

const deleteTask = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await axios.delete(`/api/v1/tasks/${row.id}`)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    in_progress: 'primary',
    completed: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return texts[status] || status
}

onMounted(() => {
  loadTasks()
  loadIterations()
})
</script>
