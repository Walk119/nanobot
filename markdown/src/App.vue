<script setup lang="ts">
import { ref, onMounted, provide, watch } from 'vue';
import { PanelLeftClose, PanelLeft, MessageSquare } from 'lucide-vue-next';
import { useFileTree } from './composables/useFileTree';
import Sidebar from './components/Sidebar.vue';
import Editor from './components/Editor.vue';
import ChatPanel from './components/ChatPanel.vue';

// 默认路径
const currentSkillRoot = ref('nanobot/skills');

const {
  nodes,
  activeFileId,
  activeFileContent,
  expandedFolders,
  editingNodeId,
  isLoading,
  activeFile,
  rootNodes,
  fetchNodes,
  toggleFolder,
  createNode,
  deleteNode,
  renameNode,
  updateContent
} = useFileTree(currentSkillRoot.value);

const isSidebarOpen = ref(true);
const isChatOpen = ref(false);

// 将操作通过 provide 提供给深层的 TreeNode 组件
provide('tree-actions', {
  nodes,
  activeFileId,
  expandedFolders,
  editingNodeId,
  toggleFolder,
  createNode,
  deleteNode,
  renameNode,
  setActiveFile: (id: string) => activeFileId.value = id,
  setEditingNodeId: (id: string | null) => editingNodeId.value = id
});

const handleRefresh = async () => {
  console.log("App.vue: Refreshing data for path:", currentSkillRoot.value);
  await fetchNodes();
};

onMounted(async () => {
  console.log("App.vue: Initializing data fetch...");
  await fetchNodes();
  console.log("App.vue: Data fetched successfully");
});
</script>

<template>
  <div class="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden font-sans">

    <!-- Sidebar -->
    <Sidebar
      v-if="isSidebarOpen"
      :rootNodes="rootNodes"
      :isLoading="isLoading"
      v-model:skillRoot="currentSkillRoot"
      @refresh="handleRefresh"
      @createNode="createNode"
    />

    <!-- Editor and Chat Container -->
    <div class="flex-1 flex min-w-0 overflow-hidden bg-white">
      <Editor
        :activeFile="activeFile"
        :content="activeFileContent"
        @updateContent="updateContent"
        @createNode="createNode"
      >
        <template #sidebar-toggle>
          <button @click="isSidebarOpen = !isSidebarOpen" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors" title="Toggle Sidebar">
            <PanelLeftClose v-if="isSidebarOpen" :size="18" />
            <PanelLeft v-else :size="18" />
          </button>
        </template>

        <template #header-right>
          <button
            v-if="activeFile"
            @click="isChatOpen = !isChatOpen"
            class="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
            :class="{ 'text-blue-600 bg-blue-50': isChatOpen }"
            title="Open AI Chat"
          >
            <MessageSquare :size="20" />
          </button>
        </template>
      </Editor>

      <!-- Chat Panel -->
      <ChatPanel
        v-if="isChatOpen"
        @close="isChatOpen = false"
      />
    </div>
  </div>
</template>

<style>
  /* 这里的全局样式（滚动条、Vditor 样式）可以保留在 App.vue 或移至单独的 CSS 文件 */
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  .vditor-container .vditor {
    border: none !important;
    border-radius: 0;
  }
  .vditor-container .vditor-toolbar {
    border-bottom: 1px solid #e2e8f0 !important;
    background-color: #f8fafc !important;
    padding: 8px 16px !important;
  }
  .vditor-container .vditor-outline {
    border-left: 1px solid #e2e8f0 !important;
    background-color: #f8fafc !important;
  }
  .vditor-container .vditor-ir {
    padding: 24px 48px !important;
    font-family: inherit !important;
  }
  .vditor-container .vditor-reset {
    font-family: inherit !important;
    color: #334155 !important;
  }
</style>
