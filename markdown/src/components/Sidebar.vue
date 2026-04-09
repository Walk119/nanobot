<script setup lang="ts">
import { ref } from 'vue';
import { FileBox, FilePlus, FolderPlus, Folder, Settings2 } from 'lucide-vue-next';
import TreeNode from './TreeNode.vue';
import type { Node } from '../api/types';
import { skillRoot } from '../store/settings'; // 引入全局状态

const props = defineProps<{
  rootNodes: Node[];
  isLoading: boolean;
}>();

const emit = defineEmits(['createNode', 'refresh']);

const handleRootChange = () => {
  // 直接操作全局响应式变量
  // 逻辑可以在这里处理，或者通过 watch 监听 skillRoot 的变化
  emit('refresh');
};
</script>

<template>
  <div class="w-64 md:w-72 flex-shrink-0 border-r border-slate-200 bg-slate-50/80 flex flex-col backdrop-blur-sm shadow-sm z-10">
    <!-- Header -->
    <div class="h-auto border-b border-slate-200 flex flex-col px-4 py-3 shrink-0 bg-slate-100/50 gap-3">
      <div class="flex items-center justify-between">
        <button
          @click="handleRootChange"
          class="flex items-center gap-2 group hover:text-blue-600 transition-colors"
        >
          <Folder :size="18" class="text-blue-600 group-hover:scale-110 transition-transform" />
          <span class="font-bold text-sm tracking-wide text-slate-800 uppercase">Skill Root</span>
        </button>
        <div class="flex gap-1">
          <button @click="(e) => emit('createNode', 'file', null, e)" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors" title="New Root File"><FilePlus :size="16" /></button>
          <button @click="(e) => emit('createNode', 'folder', null, e)" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors" title="New Root Folder"><FolderPlus :size="16" /></button>
        </div>
      </div>

      <!-- Path Input Field -->
      <div class="relative group">
        <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors">
          <Settings2 :size="14" />
        </div>
        <input
          v-model="skillRoot"
          type="text"
          spellcheck="false"
          placeholder="Path to skills..."
          @keyup.enter="handleRootChange"
          @blur="handleRootChange"
          class="w-full bg-white border border-slate-200 rounded-md py-1.5 pl-8 pr-3 text-xs font-mono text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
        />
      </div>
    </div>

    <!-- Tree Content -->
    <div class="flex-1 overflow-y-auto py-2 px-1 custom-scrollbar">
      <div v-if="isLoading" class="flex justify-center p-8">
         <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
      </div>
      <template v-else>
        <TreeNode v-for="node in rootNodes" :key="node.path" :node="node" :depth="0" :path="node.path" />
        <div v-if="rootNodes.length === 0" class="text-center p-4 text-sm text-slate-500 mt-4">
          <FileBox :size="24" class="mx-auto mb-2 text-slate-300" />
          <p>No files found in this root.</p>
          <p class="text-xs mt-1 text-slate-400">Check the path or create a file.</p>
        </div>
      </template>
    </div>
  </div>
</template>
