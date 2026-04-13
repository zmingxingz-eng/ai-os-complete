<template>
  <PageContainer title="组织管理" description="维护组织树、负责人、临时标记与组织全路径。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="组织名称/编码" style="width: 240px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table
      :data="treeData"
      v-loading="loading"
      border
      row-key="id"
      empty-text="暂无组织数据"
      :expand-row-keys="expandedRowKeys"
      :tree-props="{ children: 'children' }"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="组织名称" min-width="180" />
      <el-table-column label="组织类型" width="120">
        <template #default="{ row }">
          <el-tag>{{ orgKindLabelMap[row.org_kind] || row.org_kind }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="code" label="组织编码" min-width="140" />
      <el-table-column prop="path_name" label="全路径" min-width="220" show-overflow-tooltip />
      <el-table-column prop="leader_name" label="负责人" min-width="120" />
      <el-table-column label="临时机构" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_temporary ? 'warning' : 'info'">{{ row.is_temporary ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '正常' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort" label="排序" width="90" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑组织' : '新增组织'" width="620px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="组织编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="组织类型" prop="org_kind">
          <el-select v-model="form.org_kind" style="width: 100%">
            <el-option label="集团" value="group" />
            <el-option label="公司/分支机构" value="company" />
            <el-option label="部门" value="department" />
            <el-option label="小组" value="team" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级组织">
          <el-select v-model="form.parent" clearable filterable style="width: 100%">
            <el-option v-for="item in parentOptions" :key="item.id" :label="item.path_name || item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="form.leader" clearable filterable style="width: 100%">
            <el-option
              v-for="item in leaderOptions"
              :key="item.id"
              :label="`${item.full_name || item.username}（${item.username}）`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="临时机构">
          <el-switch v-model="form.is_temporary" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="正常" value="active" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { createOrganization, deleteOrganization, fetchOrganizationList, updateOrganization } from '@/api/system/organization'
import { fetchUsersList } from '@/api/system/users'
import { useCrud } from '@/composables/useCrud'

const orgKindLabelMap: Record<string, string> = {
  group: '集团',
  company: '公司/分支机构',
  department: '部门',
  team: '小组',
}

const keyword = ref('')
const dialogVisible = ref(false)
const leaderOptions = ref<any[]>([])
const formRef = ref<InstanceType<typeof ElForm>>()

const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchOrganizationList)
const treeData = computed(() => buildTree(filteredList.value))
const expandedRowKeys = computed(() => treeData.value.map((item: any) => item.id))
const parentOptions = computed(() => list.value.filter((item: any) => item.id !== form.id))

const form = reactive<any>({
  id: undefined,
  name: '',
  code: '',
  org_kind: 'department',
  parent: undefined,
  leader: undefined,
  is_temporary: false,
  status: 'active',
  sort: 0,
  remark: '',
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入组织名称', trigger: 'blur' },
    { min: 2, max: 50, message: '组织名称长度为 2-50 位', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入组织编码', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9_]*$/, message: '组织编码仅支持字母、数字和下划线，且需以字母开头', trigger: 'blur' },
  ],
  org_kind: [{ required: true, message: '请选择组织类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  sort: [{ required: true, message: '请输入排序', trigger: 'change' }],
}

const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    String(item.name || '').includes(keyword.value) ||
    String(item.code || '').includes(keyword.value)
  )
})

const buildTree = (items: any[]) => {
  const map = new Map<number, any>()
  const roots: any[] = []
  items.forEach((item) => map.set(item.id, { ...item, children: [] }))
  items.forEach((item) => {
    const current = map.get(item.id)
    if (item.parent && map.has(item.parent)) {
      map.get(item.parent).children.push(current)
    } else {
      roots.push(current)
    }
  })
  return roots
}

const loadLeaderOptions = async () => {
  const payload = await fetchUsersList({ page_size: 1000, is_active: true }).catch(() => [])
  leaderOptions.value = Array.isArray(payload) ? payload : payload?.results || []
}

const handleReset = () => {
  keyword.value = ''
  fetchList()
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.code = ''
  form.org_kind = 'department'
  form.parent = undefined
  form.leader = undefined
  form.is_temporary = false
  form.status = 'active'
  form.sort = 0
  form.remark = ''
}

const openCreate = async () => {
  resetForm()
  await loadLeaderOptions()
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const openEdit = async (row: any) => {
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.org_kind = row.org_kind || 'department'
  form.parent = row.parent
  form.leader = row.leader
  form.is_temporary = row.is_temporary
  form.status = row.status || (row.is_active ? 'active' : 'disabled')
  form.sort = row.sort
  form.remark = row.remark || ''
  await loadLeaderOptions()
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    name: form.name,
    code: form.code,
    org_kind: form.org_kind,
    parent: form.parent || null,
    leader: form.leader || null,
    is_temporary: form.is_temporary,
    status: form.status,
    is_active: form.status === 'active',
    sort: form.sort,
    remark: form.remark,
  }
  if (form.id) {
    await updateOrganization(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createOrganization(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除组织【${row.name}】吗？`, '提示')
  await deleteOrganization(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
