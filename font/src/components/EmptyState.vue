<script setup lang="ts">
import { FileBox, Plus } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'create-file'): void
}>()
</script>

<template>
  <div class="flex-1 flex items-center justify-center bg-slate-50/50 text-slate-400">
    <div class="text-center max-w-sm px-6">
      <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm border border-slate-200">
        <FileBox :size="40" class="text-slate-300" />
      </div>
      <h3 class="text-xl font-medium text-slate-700 mb-2">No File Selected</h3>
      <p class="text-slate-500 mb-6 text-sm leading-relaxed">
        Select a markdown file from the sidebar to start writing, or create a new file to capture your thoughts.
      </p>
      <button 
        @click="emit('create-file')"
        class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm inline-flex items-center gap-2"
      >
        <Plus :size="16" />
        Create New File
      </button>
    </div>
  </div>
</template>