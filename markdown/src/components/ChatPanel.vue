<script setup lang="ts">
import { X } from 'lucide-vue-next';

const emit = defineEmits(['close']);
</script>

<template>
  <div
    class="w-80 md:w-96 border-l border-slate-200 bg-slate-50 flex flex-col shadow-[-4px_0_15px_-3px_rgba(0,0,0,0.05)] transition-all duration-300 animate-in slide-in-from-right"
  >
    <!-- Panel Header -->
    <div class="h-12 px-4 border-b border-slate-200 flex items-center justify-between bg-white shrink-0">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-500">AI Chat Assistant</span>
      <button @click="emit('close')" class="p-1 hover:bg-slate-100 rounded text-slate-400">
        <X :size="14" />
      </button>
    </div>

    <!-- Panel Content -->
    <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar">
      <div class="bg-white p-3 rounded-lg border border-slate-200 text-sm text-slate-600 shadow-sm">
         Hello! I am your AI assistant. How can I help you with this document?
      </div>
      <!-- 这里之后可以放置对话列表 -->
    </div>

    <!-- Panel Input -->
    <div class="p-3 border-t border-slate-200 bg-white">
      <div class="relative">
        <input
          type="text"
          placeholder="Ask anything..."
          class="w-full bg-slate-50 border border-slate-200 rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation-duration: 0.2s;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-in-from-right {
  animation-name: slideInRight;
}
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
