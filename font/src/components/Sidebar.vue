<script setup lang="ts">
import { computed } from 'vue'
import { FileBox, FilePlus, FolderPlus } from 'lucide-vue-next'
import TreeNode from './TreeNode.vue'

interface Node {
  id: string
  name: string
  type: 'file' | 'folder'
  parentId: string | null
  content: string
  createdAt: number
  updatedAt: number
}

const props = defineProps<{
  isLoading: boolean
  nodes: Node[]
  expandedFolders: Set<string>
  editingNodeId: string | null
  activeFileId: string | null
  editValues: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'toggle-folder', folderId: string, forceExpand?: boolean): void
  (e: 'create-node', type: 'file' | 'folder', parentId: string | null, event?: MouseEvent): void
  (e: 'start-editing', nodeId: string, event: Event): void
  (e: 'rename-node', nodeId: string, newName: string): void
  (e: 'delete-node', id: string, event?: MouseEvent): void
  (e: 'handle-edit-keydown', event: KeyboardEvent, nodeId: string): void
  (e: 'handle-edit-blur', nodeId: string): void
  (e: 'update:edit-values', value: Record<string, string>): void
}>()

const sortedRootNodes = computed(() => {
  return props.nodes
    .filter(n => n.parentId === null)
    .sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
      return a.name.localeCompare(b.name)
    })
})
</script>

<template>
  <div class="w-64 md:w-72 flex-shrink-0 border-r border-slate-200 bg-slate-50/80 flex flex-col backdrop-blur-sm shadow-sm z-10">
    <div class="h-12 border-b border-slate-200 flex items-center justify-between px-4 shrink-0 bg-slate-100/50">
      <div class="flex items-center gap-2">
        <FileBox :size="18" class="text-blue-600" />
        <span class="font-semibold text-sm tracking-wide text-slate-800 uppercase">Explorer</span>
      </div>
      <div class="flex gap-1.5">
        <button 
          @click.stop="emit('create-node', 'file', null, $event)" 
          class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors"
          title="New Root File"
        >
          <FilePlus :size="16" />
        </button>
        <button 
          @click.stop="emit('create-node', 'folder', null, $event)" 
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
          @toggle-folder="(folderId, forceExpand) => emit('toggle-folder', folderId, forceExpand)"
          @create-node="(type, parentId, event) => emit('create-node', type, parentId, event)"
          @start-editing="(nodeId, event) => emit('start-editing', nodeId, event)"
          @rename-node="(nodeId, newName) => emit('rename-node', nodeId, newName)"
          @delete-node="(id, event) => emit('delete-node', id, event)"
          @handle-edit-keydown="(event, nodeId) => emit('handle-edit-keydown', event, nodeId)"
          @handle-edit-blur="(nodeId) => emit('handle-edit-blur', nodeId)"
          @update:edit-values="(value) => emit('update:edit-values', value)"
        />
      </template>
      <div v-else class="text-center p-4 text-sm text-slate-500 mt-4">
        No files yet. Create one to get started!
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
</style>