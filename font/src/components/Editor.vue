<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'

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
  activeFile: Node | undefined
}>()

const emit = defineEmits<{
  (e: 'update-content', id: string, content: string): void
}>()

const vditorContainerRef = ref<HTMLElement | null>(null)
let vditorInstance: Vditor | null = null

const initVditor = () => {
  if (!vditorContainerRef.value || !props.activeFile) return

  vditorInstance = new Vditor(vditorContainerRef.value, {
    height: '100%',
    mode: 'ir', // Instant Rendering (Typora-like style)
    cache: { enable: false }, // We handle our own state via `nodes`
    value: props.activeFile.content,
    outline: {
      enable: true,
      position: 'right',
    },
    toolbarConfig: {
      pin: true,
    },
    input: (value) => {
      if (props.activeFile) {
        emit('update-content', props.activeFile.id, value)
      }
    },
  })
}

const destroyVditor = () => {
  if (vditorInstance) {
    vditorInstance.destroy()
    vditorInstance = null
  }
}

// Watch for active file changes
watch(() => props.activeFile, async (newFile) => {
  destroyVditor()
  await nextTick()
  if (newFile) {
    initVditor()
  }
}, { immediate: true })

onMounted(() => {
  if (props.activeFile) {
    initVditor()
  }
})

onUnmounted(() => {
  destroyVditor()
})
</script>

<template>
  <div class="flex-1 flex overflow-hidden">
    <div class="w-full h-full relative vditor-container">
      <div ref="vditorContainerRef" class="absolute inset-0 border-none" />
    </div>
  </div>
</template>

<style scoped>
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