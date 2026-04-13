<template>
  <PageContainer title="个人中心" description="查看并维护当前登录用户的基础资料。">
    <template #actions>
      <el-button type="primary" @click="editing = !editing">{{ editing ? '取消编辑' : '编辑资料' }}</el-button>
    </template>

    <el-form
      v-if="editing"
      ref="formRef"
      :model="form"
      :rules="formRules"
      label-width="100px"
      class="profile-form"
    >
      <el-form-item label="账号">
        <el-input v-model="form.username" disabled />
      </el-form-item>
      <el-form-item label="姓名" prop="full_name">
        <el-input v-model="form.full_name" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="手机号" prop="mobile">
        <el-input v-model="form.mobile" />
      </el-form-item>
      <el-form-item label="任职岗位">
        <el-input v-model="form.position_name" disabled />
      </el-form-item>
      <el-form-item label="隶属组织">
        <el-input v-model="form.organization_name" disabled />
      </el-form-item>
      <el-form-item>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存资料</el-button>
      </el-form-item>
    </el-form>

    <el-descriptions v-else :column="2" border>
      <el-descriptions-item label="姓名">{{ sessionInfo.full_name || '-' }}</el-descriptions-item>
      <el-descriptions-item label="账号">{{ sessionInfo.username || '-' }}</el-descriptions-item>
      <el-descriptions-item label="隶属组织">{{ sessionInfo.organization_name || '-' }}</el-descriptions-item>
      <el-descriptions-item label="任职岗位">{{ sessionInfo.position_name || '-' }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ sessionInfo.email || '-' }}</el-descriptions-item>
      <el-descriptions-item label="手机号">{{ sessionInfo.mobile || '-' }}</el-descriptions-item>
      <el-descriptions-item label="管理员">{{ sessionInfo.is_superuser ? '是' : '否' }}</el-descriptions-item>
      <el-descriptions-item label="用户 ID">{{ sessionInfo.user_id || '-' }}</el-descriptions-item>
    </el-descriptions>
  </PageContainer>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, type ElForm, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchSessionInfo } from '@/api/auth'
import { updateUser } from '@/api/system/users'

const sessionInfo = ref<Record<string, any>>({})
const editing = ref(false)
const saving = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

const form = reactive<any>({
  id: undefined,
  username: '',
  full_name: '',
  email: '',
  mobile: '',
  organization: undefined,
  position_name: '',
  position: undefined,
  organization_name: '',
})

const formRules: FormRules = {
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入有效邮箱地址', trigger: 'blur' }],
  mobile: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入有效的手机号', trigger: 'blur' },
  ],
}

const fillForm = (payload: Record<string, any>) => {
  form.id = payload.user_id
  form.username = payload.username || ''
  form.full_name = payload.full_name || ''
  form.email = payload.email || ''
  form.mobile = payload.mobile || ''
  form.organization = payload.organization
  form.position_name = payload.position_name || ''
  form.position = payload.position
  form.organization_name = payload.organization_name || ''
}

const loadProfile = async () => {
  sessionInfo.value = await fetchSessionInfo().catch(() => ({}))
  fillForm(sessionInfo.value)
}

const handleCancel = async () => {
  editing.value = false
  fillForm(sessionInfo.value)
  await nextTick()
  formRef.value?.clearValidate()
}

const handleSave = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || !form.id) return
  saving.value = true
  try {
    await updateUser(form.id, {
      username: form.username,
      full_name: form.full_name,
      email: form.email,
      mobile: form.mobile,
      organization_id: form.organization,
      position_id: form.position,
      is_active: true,
    })
    await loadProfile()
    editing.value = false
    ElMessage.success('个人资料保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-form {
  max-width: 760px;
}
</style>
