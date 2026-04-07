<template>
  <div class="file-tree-container">
    <div class="tree-header">
      <span>Project Explorer</span>
      <a-button type="text" size="mini" @click="addRootNode">
        <template #icon><icon-plus /></template>
      </a-button>
    </div>

    <a-tree
      :data="treeData"
      directory
      block-node
      :show-line="false"
      v-model:selected-keys="selectedKeys"
      v-model:expanded-keys="expandedKeys"
      @select="onSelect"
    >
      <template #icon="{ node }">
        <template v-if="!node.children">
          <icon-file-pdf v-if="node.title.endsWith('.pdf')" />
          <icon-code v-else-if="node.title.endsWith('.js') || node.title.endsWith('.vue')" />
          <icon-file v-else />
        </template>
      </template>

      <template #extra="{ node }">
        <div class="tree-actions">
          <icon-plus-circle 
            v-if="node.children" 
            @click.stop="addChildNode(node)" 
            title="新建文件"
          />
          <icon-delete 
            @click.stop="deleteNode(node.key)" 
            title="删除"
            style="margin-left: 8px; color: var(--color-danger-light-4)"
          />
        </div>
      </template>
    </a-tree>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { 
  IconFile, 
  IconFilePdf, 
  IconCode, 
  IconPlus, 
  IconPlusCircle, 
  IconDelete 
} from '@arco-design/web-vue/es/icon';

// 初始数据结构
const treeData = ref([
  {
    title: 'src',
    key: '0-0',
    children: [
      { title: 'App.vue', key: '0-0-0' },
      { title: 'main.js', key: '0-0-1' },
    ],
  },
  {
    title: 'public',
    key: '0-1',
    children: [
      { title: 'favicon.ico', key: '0-1-0' },
    ],
  },
  { title: 'README.md', key: '0-2' },
]);

const selectedKeys = ref([]);
const expandedKeys = ref(['0-0']);

// 选中文件时的回调
const onSelect = (keys, event) => {
  console.log('当前选中文件:', event.node.title);
};

// 功能：在根目录新建
const addRootNode = () => {
  const newKey = `new-${Date.now()}`;
  treeData.value.push({
    title: 'new_folder',
    key: newKey,
    children: [] // 初始为文件夹
  });
};

// 功能：在指定文件夹下新建
const addChildNode = (parentNode) => {
  if (!parentNode.children) return;
  
  const newKey = `${parentNode.key}-${Date.now()}`;
  parentNode.children.push({
    title: 'new_file.js',
    key: newKey,
  });
  // 自动展开父节点
  if (!expandedKeys.value.includes(parentNode.key)) {
    expandedKeys.value.push(parentNode.key);
  }
};

// 功能：递归删除节点
const deleteNode = (key) => {
  const remove = (data) => {
    return data.filter(item => {
      if (item.key === key) return false;
      if (item.children) {
        item.children = remove(item.children);
      }
      return true;
    });
  };
  treeData.value = remove(treeData.value);
};
</script>

<style scoped>
.file-tree-container {
  width: 300px;
  padding: 12px;
  background-color: var(--color-fill-1);
  border-right: 1px solid var(--color-border-2);
  height: 100vh;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0 4px;
  font-weight: bold;
  color: var(--color-text-1);
}

/* 仿 GitHub 的悬浮操作显示 */
.tree-actions {
  display: none; /* 默认隐藏 */
  align-items: center;
  padding-right: 8px;
}

:deep(.arco-tree-node:hover) .tree-actions {
  display: flex; /* 悬浮时显示 */
}

:deep(.arco-tree-node-title) {
  font-size: 13px;
}

/* 调整选中态颜色 */
:deep(.arco-tree-node-selected) {
  background-color: var(--color-fill-3);
}
</style>