<script setup lang="ts">
import { PanelLeftClose, PanelLeft, FileText, MessageSquare } from 'lucide-vue-next'

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
  isSidebarOpen: boolean
  activeFile: Node | undefined
  activePage: 'editor' | 'botchat'
}>()

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
  (e: 'page-change', page: 'editor' | 'botchat'): void
}>()
</script>

<template>
  <div class="h-12 border-b border-slate-200 bg-white flex items-center px-4 justify-between shrink-0 shadow-sm z-10 relative">
    <div class="flex items-center gap-4">
      <button 
        @click="emit('toggle-sidebar')" 
        class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors"
        title="Toggle Sidebar"
      >
        <component :is="isSidebarOpen ? PanelLeftClose : PanelLeft" :size="18" />
      </button>
      
      <div 
        v-if="activeFile && activePage === 'editor'" 
        class="flex items-center gap-2 px-2 py-1 bg-blue-50/50 rounded-md border border-blue-100"
      >
        <FileText :size="16" class="text-blue-500" />
        <span class="text-sm font-medium text-slate-700">
          {{ activeFile.name }}
        </span>
      </div>
    </div>
    
    <!-- Page Navigation -->
    <div class="flex items-center gap-2">
      <button 
        @click="emit('page-change', 'editor')"
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors"
        :class="activePage === 'editor' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:bg-slate-100'"
      >
        <FileText :size="16" />
        <span>编辑器</span>
      </button>
      <button 
        @click="emit('page-change', 'botchat')"
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors"
        :class="activePage === 'botchat' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:bg-slate-100'"
      >
        <MessageSquare :size="16" />
        <span>聊天</span>
      </button>
    </div>
  </div>
</template>