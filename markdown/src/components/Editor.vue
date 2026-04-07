<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import Vditor from 'vditor';
import 'vditor/dist/index.css';
import { FileText, FileBox, Plus } from 'lucide-vue-next';
import type { Node } from '../api/types';

const props = defineProps<{
  activeFile: Node | undefined;
  content: string;
}>();

const emit = defineEmits(['updateContent', 'createNode']);

const vditorRef = ref<HTMLDivElement | null>(null);
let vditorInstance: Vditor | null = null;

const initVditor = () => {
  if (!vditorRef.value || !props.activeFile) return;

  if (vditorInstance) {
    vditorInstance.destroy();
    vditorInstance = null;
  }

  console.log("init vditor");
  vditorInstance = new Vditor(vditorRef.value, {
    height: '100%',
    mode: 'ir',
    cache: { enable: false },
    value: props.content,
    outline: { enable: true, position: 'right' },
    toolbarConfig: { pin: true },
    input: (value) => {
        emit('updateContent', props.activeFile?.path, value);
    }
  });
};

watch(() => props.activeFile?.path, (newPath) => {
  if (newPath) {
    nextTick(initVditor);
  } else if (vditorInstance) {
    vditorInstance.destroy();
    vditorInstance = null;
  }
});

watch(() => props.content, (newContent) => {
    if (vditorInstance && newContent !== vditorInstance.getValue()) {
        vditorInstance.setValue(newContent);
    }
});

onMounted(initVditor);
onUnmounted(() => vditorInstance?.destroy());
</script>

<template>
  <div class="flex-1 flex flex-col min-w-0 bg-white">
    <!-- Header -->
    <div class="h-12 border-b border-slate-200 bg-white flex items-center px-4 justify-between shrink-0 shadow-sm z-10 relative">
      <div class="flex items-center gap-4">
        <slot name="sidebar-toggle"></slot>
        <div v-if="activeFile" class="flex items-center gap-2 px-2 py-1 bg-blue-50/50 rounded-md border border-blue-100">
          <FileText :size="16" class="text-blue-500" />
          <span class="text-sm font-medium text-slate-700">{{ activeFile.name }}</span>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-if="activeFile" class="flex-1 flex overflow-hidden">
      <div class="w-full h-full relative vditor-container">
        <div ref="vditorRef" class="absolute inset-0 border-none" />
      </div>
    </div>
    <div v-else class="flex-1 flex items-center justify-center bg-slate-50/50 text-slate-400">
      <div class="text-center max-w-sm px-6">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm border border-slate-200">
          <FileBox :size="40" class="text-slate-300" />
        </div>
        <h3 class="text-xl font-medium text-slate-700 mb-2">No File Selected</h3>
        <p class="text-slate-500 mb-6 text-sm leading-relaxed">
          Select a markdown file from the sidebar to start writing.
        </p>
        <button
          @click="(e) => emit('createNode', 'file', null, e)"
          class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm inline-flex items-center gap-2"
        >
          <Plus :size="16" />
          Create New File
        </button>
      </div>
    </div>
  </div>
</template>
