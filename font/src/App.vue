<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSkillTree } from './composables/useSkillTree'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import Editor from './components/Editor.vue'
import EmptyState from './components/EmptyState.vue'
import BotChat from './components/botchat.vue'

// 使用技能树 composable（包含所有业务逻辑）
const skillTree = useSkillTree()

// Local State (UI 状态)
const isSidebarOpen = ref(true)
const expandedFolders = ref<Set<string>>(new Set())
const activePage = ref('editor') // 'editor' 或 'botchat'

// Derived state
const activeFile = computed(() => {
  return skillTree.nodes.value.find(n => n.id === skillTree.activeFileId.value && n.type === 'file')
})

// Initialize and load data
onMounted(async () => {
  const result = await skillTree.loadFromServer()
  console.log('Loaded from server:')
  console.log(result)
  
  // 设置初始状态
  expandedFolders.value = new Set(result.expandedFolders)
  skillTree.activeFileId.value = result.firstFileId
})

// UI Handlers (只负责调用 composable 中的逻辑)
const handleToggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const handleCreateFile = () => {
  skillTree.createNode('file', null, expandedFolders.value)
}

const handleLoadFileContent = async (fileId: string, fileName: string) => {
  await skillTree.loadFileContent(fileId, fileName)
}

const handlePageChange = (page: 'editor' | 'botchat') => {
  activePage.value = page
}
</script>

<template>
  <div class="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden font-sans">
    <!-- Sidebar -->
    <Sidebar 
      v-if="isSidebarOpen"
      :is-loading="skillTree.isLoading.value"
      :nodes="skillTree.nodes.value"
      :expanded-folders="expandedFolders"
      :editing-node-id="skillTree.editingNodeId.value"
      :active-file-id="skillTree.activeFileId.value"
      :edit-values="skillTree.editValues.value"
      @toggle-folder="(folderId, forceExpand) => skillTree.toggleFolder(expandedFolders, folderId, forceExpand)"
      @create-node="(type, parentId) => skillTree.createNode(type, parentId, expandedFolders)"
      @start-editing="skillTree.startEditing"
      @rename-node="skillTree.renameNode"
      @delete-node="(id) => skillTree.deleteNode(id, expandedFolders)"
      @handle-edit-keydown="skillTree.handleEditKeydown"
      @handle-edit-blur="skillTree.handleEditBlur"
      @update:edit-values="skillTree.editValues = $event"
    />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 bg-white">
      <!-- Top Header -->
      <Header 
        :is-sidebar-open="isSidebarOpen"
        :active-file="activeFile"
        :active-page="activePage"
        @toggle-sidebar="handleToggleSidebar"
        @page-change="handlePageChange"
      />

      <!-- Editor Area (Vditor) -->
      <Editor 
        v-if="activePage === 'editor' && activeFile"
        :active-file="activeFile"
        @update-content="skillTree.updateContent"
      />
      
      <!-- Empty State -->
      <EmptyState v-else-if="activePage === 'editor' && !activeFile" @create-file="handleCreateFile" />
      
      <!-- BotChat Page -->
      <BotChat v-else-if="activePage === 'botchat'" />
    </div>
  </div>
</template>
