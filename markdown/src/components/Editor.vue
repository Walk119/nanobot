<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import Vditor from 'vditor';
import 'vditor/dist/index.css';
import { FileText, FileBox, Plus, Check, Cloud } from 'lucide-vue-next';
import type { Node } from '../api/types';

const props = defineProps<{
  activeFile: Node | undefined;
  content: string;
}>();

const emit = defineEmits(['updateContent', 'createNode']);

const vditorRef = ref<HTMLDivElement | null>(null);
let vditorInstance: Vditor | null = null;
const isVditorReady = ref(false);
const saveStatus = ref<'saved' | 'saving' | 'error'>('saved');

// 防抖保存逻辑
let saveTimeout: ReturnType<typeof setTimeout> | null = null;

const triggerSave = (path: string, value: string) => {
  saveStatus.value = 'saving';
  if (saveTimeout) clearTimeout(saveTimeout);

  saveTimeout = setTimeout(async () => {
    try {
      await emit('updateContent', path, value);
      saveStatus.value = 'saved';
    } catch (e) {
      saveStatus.value = 'error';
    }
  }, 1000); // 1秒防抖
};

const initVditor = () => {
  if (!vditorRef.value || !props.activeFile) return;

  if (vditorInstance) {
    vditorInstance.destroy();
    vditorInstance = null;
  }

  isVditorReady.value = false;

  console.log("init vditor");
  vditorInstance = new Vditor(vditorRef.value, {
    height: '100%',
    mode: 'ir',
    cache: { enable: false },
    value: props.content,
    outline: { enable: true, position: 'right' },
    toolbarConfig: { pin: true },
    after: () => {
      isVditorReady.value = true;
      if (vditorInstance && props.content !== vditorInstance.getValue()) {
        vditorInstance.setValue(props.content);
      }
    },
    input: (value) => {
        if (props.activeFile) {
            triggerSave(props.activeFile.path, value);
        }
    }
  });
};

watch(() => props.activeFile?.path, (newPath) => {
  if (newPath) {
    nextTick(initVditor);
  } else if (vditorInstance) {
    vditorInstance.destroy();
    vditorInstance = null;
    isVditorReady.value = false;
  }
});

watch(() => props.content, (newContent) => {
    if (vditorInstance && isVditorReady.value && newContent !== vditorInstance.getValue()) {
        vditorInstance.setValue(newContent);
    }
});

onMounted(initVditor);
onUnmounted(() => {
    if (saveTimeout) clearTimeout(saveTimeout);
    vditorInstance?.destroy();
});
</script>

<template>
  <div class="flex-1 flex flex-col min-w-0 bg-white relative">
    <!-- Header -->
    <div class="h-12 border-b border-slate-200 bg-white flex items-center px-4 justify-between shrink-0 shadow-sm z-10 relative">
      <div class="flex items-center gap-4">
        <slot name="sidebar-toggle"></slot>
        <div v-if="activeFile" class="flex items-center gap-2 px-2 py-1 bg-blue-50/50 rounded-md border border-blue-100">
          <FileText :size="16" class="text-blue-500" />
          <span class="text-sm font-medium text-slate-700">{{ activeFile.name }}</span>

          <!-- Save Status Indicator -->
          <div class="flex items-center ml-2 border-l border-blue-100 pl-2">
            <template v-if="saveStatus === 'saving'">
              <Cloud :size="14" class="text-blue-400 animate-pulse" />
              <span class="text-[10px] text-blue-400 ml-1">Saving...</span>
            </template>
            <template v-else-if="saveStatus === 'saved'">
              <Check :size="14" class="text-emerald-500" />
              <span class="text-[10px] text-emerald-500 ml-1">Saved</span>
            </template>
            <template v-else>
              <span class="text-[10px] text-red-500 ml-1">Error</span>
            </template>
          </div>
        </div>
      </div>

      <!-- Slot for right-aligned header content -->
      <div class="flex items-center gap-2">
        <slot name="header-right"></slot>
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
