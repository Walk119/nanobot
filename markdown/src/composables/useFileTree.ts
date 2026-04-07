import { ref, computed, watch} from 'vue';
import { api } from '../api/client';
import type { Node, NodeType } from '../api/types';

export function useFileTree() {
  const nodes = ref<Node[]>([]);
  const activeFileId = ref<string | null>(null);
  const activeFileContent = ref<string>('');
  const expandedFolders = ref<Set<string>>(new Set());
  const editingNodeId = ref<string | null>(null);
  const isLoading = ref(true);

  const activeFile = computed(() => {
    const findActiveFile = (nodeList: Node[]): Node | undefined => {
      for (const node of nodeList) {
        if (node.path === activeFileId.value && (node.type === 'file' || node.type === 'directory')) {
          return node;
        }
        if (node.children && node.children.length > 0) {
          const found = findActiveFile(node.children);
          if (found) return found;
        }
      }
      return undefined;
    };
    return findActiveFile(nodes.value);
  });

  const fetchNodes = async () => {
    try {
      isLoading.value = true;
      const data = await api.getNodes();
      console.log("get nodes from server")
      
      // 直接使用嵌套结构
      nodes.value = Array.isArray(data) ? data : (data.children || []);
      
      if (nodes.value.length > 0 && !activeFileId.value) {
        // 递归查找第一个文件
        const findFirstFile = (nodeList: Node[]): Node | undefined => {
          for (const node of nodeList) {
            if (node.type === 'file') return node;
            if (node.children && node.children.length > 0) {
              const found = findFirstFile(node.children);
              if (found) return found;
            }
          }
          return undefined;
        };
        const firstFile = findFirstFile(nodes.value);
        if (firstFile) activeFileId.value = firstFile.id;
      }
      console.log(nodes.value)
      console.log(activeFileId.value)
    } catch (error) {
      console.error('Failed to load nodes:', error);
    } finally {
      isLoading.value = false;
    }
  };

  const toggleFolder = (folderId: string, forceExpand?: boolean) => {
      console.log(folderId)
      console.log(forceExpand)
    const next = new Set(expandedFolders.value);
    if (next.has(folderId) && !forceExpand) next.delete(folderId);
    else next.add(folderId);
    expandedFolders.value = next;
  };

  // 递归查找并修改节点
  const findAndModifyNode = (nodeList: Node[], path: string, modifier: (node: Node) => void): boolean => {
    for (let i = 0; i < nodeList.length; i++) {
      if (nodeList[i].path === path) {
        modifier(nodeList[i]);
        return true;
      }
      if (nodeList[i].children && nodeList[i].children.length > 0) {
        if (findAndModifyNode(nodeList[i].children, path, modifier)) {
          return true;
        }
      }
    }
    return false;
  };

  const createNode = async (type: NodeType, parentId: string | null = null, e?: MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      const newNodeData: Partial<Node> = {
        name: type === 'folder' ? 'New Folder' : 'Untitled.md',
        type,
        parentId,
        content: type === 'file' ? '# Untitled\n\n' : '',
      };

      const createdNode = await api.createNode(newNodeData);
      
      // 添加到相应位置
      if (parentId) {
        // 找到父节点并添加到 children
        findAndModifyNode(nodes.value, parentId, (parentNode) => {
          if (!parentNode.children) parentNode.children = [];
          parentNode.children.push(createdNode);
        });
        toggleFolder(parentId, true);
      } else {
        // 添加到根节点
        nodes.value.push(createdNode);
      }
      
      editingNodeId.value = createdNode.id;
      if (type === 'file') activeFileId.value = createdNode.id;
    } catch (error) {
      console.error('Failed to create node:', error);
    }
  };

  // 递归查找并删除节点
  const findAndDeleteNode = (nodeList: Node[], path: string): boolean => {
    for (let i = 0; i < nodeList.length; i++) {
      if (nodeList[i].path === path) {
        nodeList.splice(i, 1);
        return true;
      }
      if (nodeList[i].children && nodeList[i].children.length > 0) {
        if (findAndDeleteNode(nodeList[i].children, path)) {
          return true;
        }
      }
    }
    return false;
  };

  const deleteNode = async (path: string, e?: MouseEvent) => {
    if (e) e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this item?')) return;

    try {
      await api.deleteNode(path);
      // 从嵌套结构中删除节点
      findAndDeleteNode(nodes.value, path);
      if (activeFileId.value === path) activeFileId.value = null;
    } catch (error) {
      console.error('Failed to delete node:', error);
    }
  };

  const renameNode = async (path: string, newName: string) => {
    try {
      const name = newName || (() => {
        let node: Node | undefined;
        findAndModifyNode(nodes.value, path, (n) => { node = n; });
        return node?.type === 'folder' || node?.type === 'directory' ? 'New Folder' : 'Untitled.md';
      })();
      
      const updatedNode = await api.updateNode(path, { name });
      
      // 更新节点名称
      findAndModifyNode(nodes.value, path, (node) => {
        node.name = updatedNode.name;
      });
      
      editingNodeId.value = null;
    } catch (error) {
      console.error('Failed to rename node:', error);
    }
  };

  const updateContent = async (path: string, content: string) => {
    try {
      // 更新本地内容
      findAndModifyNode(nodes.value, path, (node) => {
        node.content = content;
        node.updatedAt = Date.now();
      });
      
      await api.updateContent(path, content);
    } catch (error) {
      console.error('Failed to update content:', error);
    }
  };
  const fetchFileContent = async (path: string) => {
      try {
          console.log(path);
          const content = await api.fileContent(path);
          return content;
    } catch (error) {
      console.error('Failed to fetch file content:', error);
      return '';
    }
  };
  watch(activeFileId, async(newPath) => {
      console.log(newPath)
    if (newPath) {
        activeFileContent.value = await fetchFileContent(newPath);
    } else {
        activeFileContent.value = '';
    }
  });
  const rootNodes = computed(() => nodes.value.sort((a, b) => {
    if (a.type !== b.type) return (a.type === 'folder' || a.type === 'directory') ? -1 : 1;
    return a.name.localeCompare(b.name);
  }));

  return {
    nodes,
    activeFileId,
    activeFileContent,
    expandedFolders,
    editingNodeId,
    isLoading,
    activeFile,
    rootNodes,
    fetchNodes,
    toggleFolder,
    createNode,
    deleteNode,
    renameNode,
    updateContent,
  };
}