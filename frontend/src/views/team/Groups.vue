<template>
  <div>
    <h2>小组管理</h2>
    <el-button type="primary" @click="showAddDialog = true">新增小组</el-button>
    <el-table :data="groups" style="width: 100%; margin-top: 20px">
      <el-table-column prop="name" label="组名" />
      <el-table-column label="组长">
        <template #default="scope">
          {{ getPersonName(scope.row.leader_id) }}
        </template>
      </el-table-column>
      <el-table-column label="成员数">
        <template #default="scope">
          {{ scope.row.members?.length || 0 }} 人
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320">
        <template #default="scope">
          <el-button size="small" @click="editGroup(scope.row)">编辑</el-button>
          <el-button size="small" @click="manageMembers(scope.row)">成员管理</el-button>
          <el-button size="small" @click="manageKeyPersons(scope.row)">关键人物</el-button>
          <el-button size="small" type="danger" @click="deleteGroup(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑小组' : '新增小组'">
      <el-form :model="form" label-width="80px">
        <el-form-item label="组名" required>
          <el-input v-model="form.name" placeholder="请输入组名" />
        </el-form-item>
        <el-form-item label="组长">
          <PersonSelect v-model="form.leader_id" placeholder="选择组长" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGroup">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="showMembersDialog" title="成员管理" width="600px">
      <div style="margin-bottom: 16px;">
        <PersonSelect 
          v-model="newMemberIds" 
          :multiple="true" 
          placeholder="选择要添加的成员"
          style="width: 400px; margin-right: 8px;"
        />
        <el-button type="primary" @click="addMembers">添加成员</el-button>
      </div>
      
      <el-table :data="groupMembers" style="width: 100%;">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="employee_id" label="工号" />
        <el-table-column prop="position" label="职位" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button 
              size="small" 
              type="danger" 
              @click="removeMember(scope.row)"
              :disabled="scope.row.id === currentGroup?.leader_id"
            >
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    
    <el-dialog v-model="showKeyPersonsDialog" title="关键人物管理" width="600px">
      <div style="margin-bottom: 16px;">
        <el-select v-model="newKeyType" placeholder="选择类型" style="width: 150px; margin-right: 8px;">
          <el-option v-for="t in keyPersonTypes" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <PersonSelect 
          v-model="newKeyPersonId" 
          placeholder="选择人员"
          style="width: 250px; margin-right: 8px;"
        />
        <el-button type="primary" @click="addKeyPerson">添加</el-button>
      </div>
      
      <el-table :data="keyPersons" style="width: 100%;">
        <el-table-column label="类型">
          <template #default="scope">
            {{ getKeyPersonTypeName(scope.row.type_id) }}
          </template>
        </el-table-column>
        <el-table-column label="人员">
          <template #default="scope">
            {{ getPersonName(scope.row.person_id) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="danger" @click="removeKeyPerson(scope.row)">移除</el-button>
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

const groups = ref([])
const persons = ref([])
const keyPersonTypes = ref([])
const showAddDialog = ref(false)
const showMembersDialog = ref(false)
const showKeyPersonsDialog = ref(false)
const isEdit = ref(false)
const currentGroup = ref(null)
const groupMembers = ref([])
const keyPersons = ref([])
const newMemberIds = ref([])
const newKeyType = ref('')
const newKeyPersonId = ref('')

const form = ref({
  id: '',
  name: '',
  leader_id: ''
})

const loadGroups = async () => {
  const res = await axios.get('/api/v1/groups')
  groups.value = res.data
}

const loadPersons = async () => {
  const res = await axios.get('/api/v1/persons')
  persons.value = res.data
}

const loadKeyPersonTypes = async () => {
  const res = await axios.get('/api/v1/key-person-types')
  keyPersonTypes.value = res.data
}

const getPersonName = (id) => {
  const person = persons.value.find(p => p.id === id)
  return person ? person.name : '-'
}

const getKeyPersonTypeName = (id) => {
  const type = keyPersonTypes.value.find(t => t.id === id)
  return type ? type.name : '-'
}

const editGroup = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    leader_id: row.leader_id || ''
  }
  showAddDialog.value = true
}

const saveGroup = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入组名')
    return
  }
  
  try {
    if (isEdit.value) {
      await axios.put(`/api/v1/groups/${form.value.id}`, {
        name: form.value.name,
        leader_id: form.value.leader_id || null
      })
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/groups', {
        name: form.value.name,
        leader_id: form.value.leader_id || null,
        member_ids: []
      })
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    loadGroups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const manageMembers = async (row) => {
  currentGroup.value = row
  
  const res = await axios.get(`/api/v1/groups/${row.id}`)
  const memberIds = res.data.members || []
  groupMembers.value = persons.value.filter(p => memberIds.includes(p.id))
  
  newMemberIds.value = []
  showMembersDialog.value = true
}

const addMembers = async () => {
  if (!newMemberIds.value || newMemberIds.value.length === 0) {
    ElMessage.warning('请选择要添加的成员')
    return
  }
  
  try {
    await axios.post(`/api/v1/groups/${currentGroup.value.id}/members`, {
      person_ids: newMemberIds.value
    })
    ElMessage.success('添加成功')
    manageMembers(currentGroup.value)
    loadGroups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  }
}

const removeMember = async (person) => {
  try {
    await ElMessageBox.confirm(`确定要移除 ${person.name} 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/groups/${currentGroup.value.id}/members/${person.id}`)
    ElMessage.success('移除成功')
    manageMembers(currentGroup.value)
    loadGroups()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '移除失败')
    }
  }
}

const manageKeyPersons = async (row) => {
  currentGroup.value = row
  
  const res = await axios.get(`/api/v1/groups/${row.id}`)
  keyPersons.value = res.data.key_persons || []
  
  newKeyType.value = ''
  newKeyPersonId.value = ''
  showKeyPersonsDialog.value = true
}

const addKeyPerson = async () => {
  if (!newKeyType.value || !newKeyPersonId.value) {
    ElMessage.warning('请选择类型和人员')
    return
  }
  
  try {
    await axios.post(`/api/v1/groups/${currentGroup.value.id}/key-persons`, {
      type_id: newKeyType.value,
      person_id: newKeyPersonId.value
    })
    ElMessage.success('添加成功')
    manageKeyPersons(currentGroup.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  }
}

const removeKeyPerson = async (kp) => {
  try {
    await ElMessageBox.confirm('确定要移除此关键人物吗?', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/groups/${currentGroup.value.id}/key-persons/${kp.id}`)
    ElMessage.success('移除成功')
    manageKeyPersons(currentGroup.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '移除失败')
    }
  }
}

const deleteGroup = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除小组 "${row.name}" 吗?`, '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/groups/${row.id}`)
    ElMessage.success('删除成功')
    loadGroups()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadGroups()
  loadPersons()
  loadKeyPersonTypes()
})
</script>
