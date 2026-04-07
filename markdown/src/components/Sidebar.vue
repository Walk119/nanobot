<script setup lang="ts">
import { FileBox, FilePlus, FolderPlus } from 'lucide-vue-next';
import TreeNode from './TreeNode.vue';
import type { Node } from '../api/types';

defineProps<{
  rootNodes: Node[];
  isLoading: boolean;
}>();

const emit = defineEmits(['createNode']);
</script>

<template>
  <div class="w-64 md:w-72 flex-shrink-0 border-r border-slate-200 bg-slate-50/80 flex flex-col backdrop-blur-sm shadow-sm z-10">
    <div class="h-12 border-b border-slate-200 flex items-center justify-between px-4 shrink-0 bg-slate-100/50">
      <div class="flex items-center gap-2">
        <FileBox :size="18" class="text-blue-600" />
        <span class="font-semibold text-sm tracking-wide text-slate-800 uppercase">Explorer</span>
      </div>
      <div class="flex gap-1.5">
        <button @click="(e) => emit('createNode', 'file', null, e)" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors" title="New Root File"><FilePlus :size="16" /></button>
        <button @click="(e) => emit('createNode', 'folder', null, e)" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors" title="New Root Folder"><FolderPlus :size="16" /></button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto py-2 px-1 custom-scrollbar">
      <div v-if="isLoading" class="flex justify-center p-8">
         <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
      </div>
      <template v-else>
        <TreeNode v-for="node in rootNodes" :key="node.path" :node="node" :depth="0" :path="node.path" />
        <div v-if="rootNodes.length === 0" class="text-center p-4 text-sm text-slate-500 mt-4">
          No files yet. Create one to get started!
        </div>
      </template>
    </div>
  </div>
</template>