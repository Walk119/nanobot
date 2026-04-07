<script setup lang="ts">
import { ref, inject, computed, nextTick, watch } from 'vue';
import {
  Folder, FolderOpen, FileText, FilePlus, FolderPlus,
  Trash2, Edit2, ChevronRight, ChevronDown
} from 'lucide-vue-next';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Node {
  id: string;
  name: string;
  type: 'file' | 'folder';
  content: string;
  children?: Node[];
}

const props = defineProps<{
  node: Node;
  depth: number;
  path: string;
}>();

const actions: any = inject('tree-actions');

const isExpanded = computed(() => actions.expandedFolders.value.has(props.path));
const isEditing = computed(() => actions.editingNodeId.value === props.path);
const isActive = computed(() => actions.activeFileId.value === props.path);
const isFolder = computed(() => props.node.type === 'folder' || props.node.type === 'directory');

const editValue = ref(props.node.name);
const inputRef = ref<HTMLInputElement | null>(null);

watch(isEditing, (val) => {
  if (val) {
    editValue.value = props.node.name;
    nextTick(() => {
      inputRef.value?.focus();
      inputRef.value?.select();
    });
  }
});

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    actions.renameNode(props.path, editValue.value);
  } else if (e.key === 'Escape') {
    actions.setEditingNodeId(null);
    editValue.value = props.node.name;
  }
};

const handleBlur = () => {
  actions.renameNode(props.path, editValue.value);
};

const childNodes = computed(() => {
  return (props.node.children || []).sort((a: Node, b: Node) => {
    if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
});

const handleClick = () => {
  if (isFolder.value) {
    actions.toggleFolder(props.path);
  } else {
    actions.setActiveFile(props.path);
  }
};
</script>

<template>
  <div class="select-none">
    <div
      :class="cn(
        'group flex items-center py-1.5 px-2 cursor-pointer text-sm transition-colors',
        isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-700 hover:bg-slate-100/80',
        isEditing && 'bg-slate-100'
      )"
      :style="{ paddingLeft: (depth * 12 + 8) + 'px' }"
      @click="handleClick"
    >
      <!-- Node Icon -->
      <div class="w-5 flex items-center justify-center mr-1.5 shrink-0">
        <template v-if="isFolder">
          <ChevronDown v-if="isExpanded" :size="14" class="text-slate-400" />
          <ChevronRight v-else :size="14" class="text-slate-400" />
        </template>
        <FileText v-else :size="14" :class="isActive ? 'text-blue-500' : 'text-slate-400'" />
      </div>

      <div v-if="isFolder" class="mr-1.5 shrink-0">
        <FolderOpen v-if="isExpanded" :size="14" class="text-blue-500" />
        <Folder v-else :size="14" class="text-blue-500" />
      </div>

      <!-- Node Label / Input -->
      <div class="flex-1 truncate min-w-0">
        <input
          v-if="isEditing"
          ref="inputRef"
          v-model="editValue"
          @keydown="handleKeyDown"
          @blur="handleBlur"
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
            @click.stop="(e) => actions.createNode('file', props.path, e)"
            class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded"
            title="New File"
          >
            <FilePlus :size="12" />
          </button>
          <button
            @click.stop="(e) => actions.createNode('folder', props.path, e)"
            class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded"
            title="New Folder"
          >
            <FolderPlus :size="12" />
          </button>
        </template>
        <button
          @click.stop="actions.setEditingNodeId(props.path)"
          class="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded"
          title="Rename"
        >
          <Edit2 :size="12" />
        </button>
        <button
          @click.stop="(e) => actions.deleteNode(props.path, e)"
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
        v-for="child in childNodes"
        :key="child.path"
        :node="child"
        :depth="depth + 1"
        :path="child.path"
      />
    </div>
  </div>
</template>