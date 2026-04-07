<script setup lang="ts">
import { ref, onMounted, provide } from 'vue';
import { PanelLeftClose, PanelLeft } from 'lucide-vue-next';
import { useFileTree } from './composables/useFileTree';
import Sidebar from './components/Sidebar.vue';
import Editor from './components/Editor.vue';

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
} = useFileTree();

const isSidebarOpen = ref(true);

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

onMounted(async () => {
  console.log("App.vue: Initializing data fetch...");
  await fetchNodes();
  console.log("App.vue: Data fetched successfully");
  console.log("Root Nodes:", rootNodes.value);
  console.log("All Nodes:", nodes.value);
});
</script>

<template>
  <div class="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden font-sans">

    <!-- Sidebar -->
    <Sidebar
      v-if="isSidebarOpen"
      :rootNodes="rootNodes"
      :isLoading="isLoading"
      @createNode="createNode"
    />

    <!-- Editor -->
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
    </Editor>
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
