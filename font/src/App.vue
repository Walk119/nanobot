<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { 
  Folder, FolderOpen, FileText, FilePlus, FolderPlus, 
  Trash2, Edit2, ChevronRight, ChevronDown, PanelLeftClose, 
  PanelLeft, FileBox, Plus
} from 'lucide-vue-next'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import TreeNode from './TreeNode.vue'
import { useSkillTree } from './composables/useSkillTree'

// Utility function for className merging
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

type NodeType = 'file' | 'folder'

interface Node {
  id: string
  name: string
  type: NodeType
  parentId: string | null
  content: string
  createdAt: number
  updatedAt: number
}

const INITIAL_NODES: Node[] = [
  {
    id: 'root-folder-1',
    name: 'Getting Started',
    type: 'folder',
    parentId: null,
    content: '',
    createdAt: Date.now(),
    updatedAt: Date.now()
  },
  {
    id: 'welcome-file',
    name: 'Welcome.md',
    type: 'file',
    parentId: 'root-folder-1',
    content: '# Welcome to Markdown Manager\n\nThis is a simple web-based Markdown editor and file manager.\n\n## Features\n\n- **File Tree**: Organize your notes into folders.\n- **Typora-like Editor**: Real-time rendering enabled using Vditor (`ir` mode).\n- **GitHub Flavored Markdown**: Supports tables, strikethrough, task lists, and more.\n\n### Code Example\n\n``js\nfunction greet() {\n  console.log("Hello World!");\n}\n```\n\n| Feature | Status |\n| :--- | :--- |\n| Create Files | ✅ |\n| Create Folders | ✅ |\n| Real-time Preview | ✅ |\n| Local State | ✅ |\n\nStart writing by creating a new file or editing this one!',
    createdAt: Date.now(),
    updatedAt: Date.now()
  },
  {
    id: 'root-folder-2',
    name: 'Personal Notes',
    type: 'folder',
    parentId: null,
    content: '',
    createdAt: Date.now(),
    updatedAt: Date.now()
  },
  {
    id: 'todo-file',
    name: 'Tasks.md',
    type: 'file',
    parentId: 'root-folder-2',
    content: '# Tasks\n\n- [x] Integrate Vditor\n- [x] Configure instant rendering (Typora style)\n- [ ] Write more notes\n',
    createdAt: Date.now(),
    updatedAt: Date.now()
  }
]

const generateId = () => Math.random().toString(36).substring(2, 11)

// 使用技能树 composable
const { nodes, isLoading, loadFromServer, loadFileContent } = useSkillTree()

// State
const activeFileId = ref<string | null>(null)
const expandedFolders = ref<Set<string>>(new Set())
const editingNodeId = ref<string | null>(null)
const isSidebarOpen = ref(true)
const editValues = ref<Record<string, string>>({})

// Vditor refs
const vditorContainerRef = ref<HTMLElement | null>(null)
let vditorInstance: Vditor | null = null

// Derived state
const activeFile = computed(() => {
  return nodes.value.find(n => n.id === activeFileId.value && n.type === 'file')
})

// Initialize and load data
onMounted(async () => {
  const result = await loadFromServer()
  
  // 设置初始状态
  expandedFolders.value = new Set(result.expandedFolders)
  activeFileId.value = result.firstFileId
  
  if (activeFile.value) {
    initVditor()
  }
})

const initVditor = () => {
  if (!vditorContainerRef.value || !activeFile.value) return

  vditorInstance = new Vditor(vditorContainerRef.value, {
    height: '100%',
    mode: 'ir', // Instant Rendering (Typora-like style)
    cache: { enable: false }, // We handle our own state via `nodes`
    value: activeFile.value.content,
    outline: {
      enable: true,
      position: 'right',
    },
    toolbarConfig: {
      pin: true,
    },
    input: (value) => {
      updateContent(activeFile.value!.id, value)
    },
  })
}

// Watch for active file changes
const watchActiveFile = async () => {
  if (vditorInstance) {
    vditorInstance.destroy()
    vditorInstance = null
  }
  
  await nextTick()
  
  if (activeFile.value) {
    // 如果是从后端加载的数据且内容为空，尝试获取文件内容
    if (!activeFile.value.content && !['welcome-file', 'todo-file'].includes(activeFile.value.id)) {
      await loadFileContent(activeFile.value.id, activeFile.value.name)
    }
    initVditor()
  }
}

onUnmounted(() => {
  if (vditorInstance) {
    vditorInstance.destroy()
    vditorInstance = null
  }
})

// Actions
const toggleFolder = (folderId: string, forceExpand?: boolean) => {
  if (forceExpand !== undefined) {
    if (forceExpand) {
      expandedFolders.value.add(folderId)
    } else {
      expandedFolders.value.delete(folderId)
    }
  } else {
    if (expandedFolders.value.has(folderId)) {
      expandedFolders.value.delete(folderId)
    } else {
      expandedFolders.value.add(folderId)
    }
  }
}

const createNode = (type: NodeType, parentId: string | null = null, event?: MouseEvent) => {
  if (event) {
    event.stopPropagation()
  }
  
  const id = generateId()
  const newNode: Node = {
    id,
    name: type === 'folder' ? 'New Folder' : 'Untitled.md',
    type,
    parentId,
    content: type === 'file' ? '# Untitled\n\n' : '',
    createdAt: Date.now(),
    updatedAt: Date.now()
  }
  
  if (parentId) {
    toggleFolder(parentId, true)
  }

  nodes.value.push(newNode)
  editingNodeId.value = id
  editValues.value[id] = newNode.name
  
  if (type === 'file') {
    activeFileId.value = id
  }
}

const getChildrenIds = (parentId: string): string[] => {
  const children = nodes.value.filter(n => n.parentId === parentId)
  let ids = children.map(c => c.id)
  for (const child of children) {
    if (child.type === 'folder') {
      ids = [...ids, ...getChildrenIds(child.id)]
    }
  }
  return ids
}

const deleteNode = (id: string, event?: MouseEvent) => {
  if (event) {
    event.stopPropagation()
  }
  if (!window.confirm('Are you sure you want to delete this item?')) return
  
  const idsToDelete = [id, ...getChildrenIds(id)]
  nodes.value = nodes.value.filter(n => !idsToDelete.includes(n.id))
  if (activeFileId.value && idsToDelete.includes(activeFileId.value)) {
    activeFileId.value = null
  }
}

const startEditing = (nodeId: string, event: Event) => {
  event.stopPropagation()
  editingNodeId.value = nodeId
  if (!editValues.value[nodeId]) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (node) {
      editValues.value[nodeId] = node.name
    }
  }
}

const renameNode = (nodeId: string, newName: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    node.name = newName || (node.type === 'folder' ? 'New Folder' : 'Untitled.md')
    node.updatedAt = Date.now()
  }
  editingNodeId.value = null
}

const updateContent = (id: string, content: string) => {
  const node = nodes.value.find(n => n.id === id)
  if (node) {
    node.content = content
    node.updatedAt = Date.now()
  }
}

const handleEditKeydown = (event: KeyboardEvent, nodeId: string) => {
  if (event.key === 'Enter') {
    renameNode(nodeId, editValues.value[nodeId])
  } else if (event.key === 'Escape') {
    editingNodeId.value = null
    editValues.value[nodeId] = nodes.value.find(n => n.id === nodeId)?.name || ''
  }
}

const handleEditBlur = (nodeId: string) => {
  renameNode(nodeId, editValues.value[nodeId])
}

const sortedRootNodes = computed(() => {
  return nodes.value
    .filter(n => n.parentId === null)
    .sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
      return a.name.localeCompare(b.name)
    })
})
</script>

<template>
  <div class="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden font-sans">
    <!-- Sidebar -->
    <div 
      v-if="isSidebarOpen" 
      class="w-64 md:w-72 flex-shrink-0 border-r border-slate-200 bg-slate-50/80 flex flex-col backdrop-blur-sm shadow-sm z-10"
    >
      <div class="h-12 border-b border-slate-200 flex items-center justify-between px-4 shrink-0 bg-slate-100/50">
        <div class="flex items-center gap-2">
          <FileBox :size="18" class="text-blue-600" />
          <span class="font-semibold text-sm tracking-wide text-slate-800 uppercase">Explorer</span>
        </div>
        <div class="flex gap-1.5">
          <button 
            @click.stop="createNode('file', null, $event)" 
            class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors"
            title="New Root File"
          >
            <FilePlus :size="16" />
          </button>
          <button 
            @click.stop="createNode('folder', null, $event)" 
            class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors"
            title="New Root Folder"
          >
            <FolderPlus :size="16" />
          </button>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto py-2 px-1 custom-scrollbar">
        <template v-if="isLoading">
          <div class="text-center p-4 text-sm text-slate-500">
            Loading skills tree...
          </div>
        </template>
        <template v-else-if="sortedRootNodes.length > 0">
          <TreeNode 
            v-for="node in sortedRootNodes" 
            :key="node.id" 
            :node="node" 
            :depth="0"
            :nodes="nodes"
            :expanded-folders="expandedFolders"
            :editing-node-id="editingNodeId"
            :active-file-id="activeFileId"
            :edit-values="editValues"
            @toggle-folder="toggleFolder"
            @create-node="createNode"
            @start-editing="startEditing"
            @rename-node="renameNode"
            @delete-node="deleteNode"
            @handle-edit-keydown="handleEditKeydown"
            @handle-edit-blur="handleEditBlur"
            @update:edit-values="editValues = $event"
          />
        </template>
        <div v-else class="text-center p-4 text-sm text-slate-500 mt-4">
          No files yet. Create one to get started!
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 bg-white">
      <!-- Top Header -->
      <div class="h-12 border-b border-slate-200 bg-white flex items-center px-4 justify-between shrink-0 shadow-sm z-10 relative">
        <div class="flex items-center gap-4">
          <button 
            @click="isSidebarOpen = !isSidebarOpen" 
            class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors"
            title="Toggle Sidebar"
          >
            <component :is="isSidebarOpen ? PanelLeftClose : PanelLeft" :size="18" />
          </button>
          
          <div 
            v-if="activeFile" 
            class="flex items-center gap-2 px-2 py-1 bg-blue-50/50 rounded-md border border-blue-100"
          >
            <FileText :size="16" class="text-blue-500" />
            <span class="text-sm font-medium text-slate-700">
              {{ activeFile.name }}
            </span>
          </div>
        </div>
      </div>

      <!-- Editor Area (Vditor) -->
      <div v-if="activeFile" class="flex-1 flex overflow-hidden">
        <div class="w-full h-full relative vditor-container">
          <div ref="vditorContainerRef" class="absolute inset-0 border-none" />
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else class="flex-1 flex items-center justify-center bg-slate-50/50 text-slate-400">
        <div class="text-center max-w-sm px-6">
          <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm border border-slate-200">
            <FileBox :size="40" class="text-slate-300" />
          </div>
          <h3 class="text-xl font-medium text-slate-700 mb-2">No File Selected</h3>
          <p class="text-slate-500 mb-6 text-sm leading-relaxed">
            Select a markdown file from the sidebar to start writing, or create a new file to capture your thoughts.
          </p>
          <button 
            @click="createNode('file', null)"
            class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm inline-flex items-center gap-2"
          >
            <Plus :size="16" />
            Create New File
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

/* Vditor overrides to match the design */
.vditor-container :deep(.vditor) {
  border: none !important;
  border-radius: 0;
}
.vditor-container :deep(.vditor-toolbar) {
  border-bottom: 1px solid #e2e8f0 !important;
  background-color: #f8fafc !important;
  padding: 8px 16px !important;
}
.vditor-container :deep(.vditor-outline) {
  border-left: 1px solid #e2e8f0 !important;
  background-color: #f8fafc !important;
}
.vditor-container :deep(.vditor-ir) {
  padding: 24px 48px !important;
  font-family: inherit !important;
}
.vditor-container :deep(.vditor-reset) {
  font-family: inherit !important;
  color: #334155 !important;
}
</style>
