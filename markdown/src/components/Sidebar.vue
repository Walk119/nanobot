<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from '../api/client';
import {
  FileBox, FilePlus, FolderPlus, Folder,
  Settings2, Plus, Trash2, ChevronDown
} from 'lucide-vue-next';
import TreeNode from './TreeNode.vue';
import type { Node, Project } from '../api/types';
import { skillRoot } from '../store/settings'; // 引入全局状态

const props = defineProps<{
  rootNodes: Node[];
  isLoading: boolean;
}>();

const emit = defineEmits(['createNode', 'refresh']);

const handleRootChange = () => {
  emit('refresh');
};

const projects = ref<Project[]>([]);
const isMenuOpen = ref(false);

const loadProjects = async () => {
  try {
    const res = await api.listProjects();
    projects.value = res.projects;
    console.log('Loaded projects:', projects.value);
    // 如果当前没有选中的 root，默认选中第一个
    if (!skillRoot.value && projects.value.length > 0) {
      handleSelect(projects.value[0].path);
    }
  } catch (e) {
    console.error('Failed to load projects', e);
  }
};

const handleSelect = (path: string) => {
  skillRoot.value = path;
  isMenuOpen.value = false;
  handleRootChange();
};

const addNewProject = async () => {
  const path = prompt('Enter new skill root path:');
  if (path) {
    await api.registerProject({ path });
    await loadProjects();
    handleSelect(path);
  }
};

const removeProject = async (path: string, e: Event) => {
  e.stopPropagation();
  if (confirm(`Remove project ${path}?`)) {
    await api.unregisterProject(path);
    await loadProjects();
    // 如果删除的是当前选中的，切换到第一个或清空
    if (skillRoot.value === path) {
      skillRoot.value = projects.value[0]?.path || '';
      handleRootChange();
    }
  }
};

onMounted(loadProjects);
</script>

<template>
  <div class="w-64 md:w-72 flex-shrink-0 border-r border-slate-200 bg-slate-50/80 flex flex-col backdrop-blur-sm shadow-sm z-10">
    <!-- Header -->
    <div class="h-auto border-b border-slate-200 flex flex-col px-4 py-3 shrink-0 bg-slate-100/50 gap-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Folder :size="18" class="text-blue-600" />
          <span class="font-bold text-sm tracking-wide text-slate-800 uppercase">Projects</span>
        </div>
        <div class="flex gap-1">
          <button @click="(e) => emit('createNode', 'file', null, e)" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors" title="New Root File"><FilePlus :size="16" /></button>
          <button @click="(e) => emit('createNode', 'folder', null, e)" class="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors" title="New Root Folder"><FolderPlus :size="16" /></button>
        </div>
      </div>

      <!-- Project Selector Dropdown -->
      <div class="relative">
        <div
          class="flex items-center justify-between bg-white border border-slate-200 rounded-md py-1.5 pl-3 pr-2 cursor-pointer hover:border-blue-500 transition-all shadow-sm"
          @click="isMenuOpen = !isMenuOpen"
        >
          <span class="text-xs font-mono text-slate-600 truncate flex-1">
            {{ skillRoot || 'Select a project...' }}
          </span>
          <div class="flex items-center gap-1 border-l pl-2 ml-2">
            <Plus :size="14" class="text-slate-400 hover:text-blue-500" @click.stop="addNewProject" />
            <ChevronDown :size="14" class="text-slate-400" :class="{ 'rotate-180': isMenuOpen }" />
          </div>
        </div>

        <!-- Dropdown Menu Content -->
        <div v-if="isMenuOpen" class="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-md shadow-lg z-50 max-h-48 overflow-y-auto overflow-x-hidden">
          <div
            v-for="p in projects"
            :key="p.path"
            class="flex items-center justify-between px-3 py-2 hover:bg-slate-50 cursor-pointer group"
            @click="handleSelect(p.path)"
          >
            <div class="flex flex-col min-w-0 pr-2">
              <span class="text-xs font-bold text-slate-700 truncate">{{ p.name }}</span>
              <span class="text-[10px] text-slate-400 truncate font-mono">{{ p.path }}</span>
            </div>
            <Trash2
              :size="12"
              class="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
              @click.stop="removeProject(p.path, $event)"
            />
          </div>
          <div v-if="projects.length === 0" class="p-3 text-center text-xs text-slate-400">
            No projects found.
          </div>
        </div>
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

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
</style>
