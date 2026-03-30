<script setup lang="ts">
import { computed } from 'vue'
import { 
  Folder, FolderOpen, FileText, FilePlus, FolderPlus, 
  Trash2, Edit2, ChevronRight, ChevronDown 
} from 'lucide-vue-next'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

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

interface Props {
  node: Node
  depth: number
  nodes: Node[]
  expandedFolders: Set<string>
  editingNodeId: string | null
  activeFileId: string | null
  editValues: Record<string, string>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleFolder: [folderId: string, forceExpand?: boolean]
  createNode: [type: NodeType, parentId: string | null, event: MouseEvent]
  startEditing: [nodeId: string, event: Event]
  renameNode: [nodeId: string, newName: string]
  deleteNode: [nodeId: string, event: MouseEvent]
  handleEditKeydown: [event: KeyboardEvent, nodeId: string]
  handleEditBlur: [nodeId: string]
  'update:activeFileId': [fileId: string | null]
  'update:editValues': [value: Record<string, string>]
}>()

const isExpanded = computed(() => props.expandedFolders.has(props.node.id))
const isEditing = computed(() => props.editingNodeId === props.node.id)
const isActive = computed(() => props.activeFileId === props.node.id)
const isFolder = computed(() => props.node.type === 'folder')

const sortedChildren = computed(() => {
  return props.nodes
    .filter(n => n.parentId === props.node.id)
    .sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
      return a.name.localeCompare(b.name)
    })
})

const handleInput = (value: string) => {
  const newEditValues = { ...props.editValues }
  newEditValues[props.node.id] = value
  emit('update:editValues', newEditValues)
}
</script>

<template>
  <div class="select-none">
    <div 
      :class="cn(
        'group flex items-center py-1.5 px-2 cursor-pointer text-sm transition-colors',
        isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-700 hover:bg-slate-100/80',
        isEditing && 'bg-slate-100'
      )"
      :style="{ paddingLeft: `${depth * 12 + 8}px` }"
      @click="isFolder ? emit('toggleFolder', node.id) : emit('update:activeFileId', node.id)"
    >
      <!-- Node Icon -->
      <div class="w-5 flex items-center justify-center mr-1.5 shrink-0">
        <component 
          :is="isFolder ? (isExpanded ? ChevronDown : ChevronRight) : FileText" 
          :size="14" 
          :class="isFolder ? 'text-slate-400' : (isActive ? 'text-blue-500' : 'text-slate-400')"
        />
      </div>
      
      <div v-if="isFolder" class="mr-1.5 shrink-0">
        <component 
          :is="isExpanded ? FolderOpen : Folder" 
          :size="14" 
          class="text-blue-500"
        />
      </div>

      <!-- Node Label / Input -->
      <div class="flex-1 truncate min-w-0">
        <input
          v-if="isEditing"
          :value="editValues[node.id] || ''"
          @input="handleInput(($event.target as HTMLInputElement).value)"
          @keydown.stop="emit('handleEditKeydown', $event, node.id)"
          @blur="emit('handleEditBlur', node.id)"
          @click.stop
          class="w-full bg-white border border-blue-400 rounded px-1 text-sm outline-none"
        />
        <span v-else :class="cn('truncate block', isActive && 'font-medium')">
          {{ node.name }}
        </span>
      </div>

      <!-- Hover Actions -->
      <div v-if="!isEditing" class="opacity-0 group-hover:opacity-100 flex items-center gap-1 shrink-0 ml-2">
        <template v-if="isFolder">
          <button 
            @click.stop="emit('createNode', 'file', node.id, $event)" 
            class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded" 
            title="New File"
          >
            <FilePlus :size="12" />
          </button>
          <button 
            @click.stop="emit('createNode', 'folder', node.id, $event)" 
            class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded" 
            title="New Folder"
          >
            <FolderPlus :size="12" />
          </button>
        </template>
        <button 
          @click.stop="emit('startEditing', node.id, $event)" 
          class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded" 
          title="Rename"
        >
          <Edit2 :size="12" />
        </button>
        <button 
          @click.stop="emit('deleteNode', node.id, $event)" 
          class="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded" 
          title="Delete"
        >
          <Trash2 :size="12" />
        </button>
      </div>
    </div>

    <!-- Render Children if Expanded Folder -->
    <div v-if="isFolder && isExpanded" class="flex flex-col">
      <TreeNode
        v-for="child in sortedChildren"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
        :nodes="nodes"
        :expanded-folders="expandedFolders"
        :editing-node-id="editingNodeId"
        :active-file-id="activeFileId"
        :edit-values="editValues"
        @toggle-folder="emit('toggleFolder', $event[0], $event[1])"
        @create-node="emit('createNode', $event[0], $event[1], $event[2])"
        @start-editing="emit('startEditing', $event[0], $event[1])"
        @rename-node="emit('renameNode', $event[0], $event[1])"
        @delete-node="emit('deleteNode', $event[0], $event[1])"
        @handle-edit-keydown="emit('handleEditKeydown', $event[0], $event[1])"
        @handle-edit-blur="emit('handleEditBlur', $event[0])"
        @update:edit-values="emit('update:editValues', $event)"
      />
    </div>
  </div>
</template>
