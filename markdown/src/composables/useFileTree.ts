import { ref, computed, watch} from 'vue';
import { api } from '../api/client';
import type { Node, NodeType } from '../api/types';

export function useFileTree() {

  const nodes = ref<Node[]>([]);
  const activeFileId = ref<string | null>(null);
  const activeFileContent = ref<string>('');
  const expandedFolders = ref<Set<string>>(new Set());
  const editingNodeId = ref<string | null>(null);
  const isLoading = ref(false);

  const activeFile = computed(() => {
    const findActiveFile = (nodeList: Node[]): Node | undefined => {
      for (const node of nodeList) {
        if (node.path === activeFileId.value && (node.type === 'file' || node.type === 'directory' || node.type === 'folder')) {
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

  const fetchNodes = async (newRoot?: string) => {
    try {
      isLoading.value = true;
      const data = await api.getNodes();

      // 直接使用嵌套结构
      nodes.value = Array.isArray(data) ? data : (data.children || []);
      
      // 如果切换了目录，且当前文件不在新列表中，重置状态
      if (newRoot && !activeFile.value) {
          activeFileId.value = null;
          activeFileContent.value = '';
      }

      if (nodes.value.length > 0 && !activeFileId.value) {
        const findFirstFileInNested = (nodeList: Node[]): Node | undefined => {
            for (const node of nodeList) {
                if (node.type === 'file') return node;
                if (node.children && node.children.length > 0) {
                    const found = findFirstFileInNested(node.children);
                    if (found) return found;
                }
            }
            return undefined;
        };
        const firstFile = findFirstFileInNested(nodes.value);
        if (firstFile) activeFileId.value = firstFile.path;
      }
    } catch (error) {
      console.error('Failed to load nodes:', error);
      nodes.value = [];
    } finally {
      isLoading.value = false;
    }
  };

  const toggleFolder = (folderId: string, forceExpand?: boolean) => {
    const next = new Set(expandedFolders.value);
    if (next.has(folderId) && !forceExpand) next.delete(folderId);
    else next.add(folderId);
    expandedFolders.value = next;
  };

  const createNode = async (type: NodeType, parentId: string | null = null, e?: MouseEvent) => {
    if (e) e.stopPropagation();
    const defaultName = type === 'folder' ? 'New Folder' : 'Untitled.md';
    const content = type === 'file' ? '# Untitled\n\n' : '';

    try {
      const newNode = await api.createNode({ name: defaultName, type, parentId, content });
      await fetchNodes();
      // 自动进入重命名模式
      editingNodeId.value = newNode.path;
      if (type === 'file') activeFileId.value = newNode.path;
      if (parentId) {
          toggleFolder(parentId, true);
      }
    } catch (error) {
      console.error('Failed to create node:', error);
    }
  };

  const deleteNode = async (path: string, e?: MouseEvent) => {
    if (e) e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this item?')) return;

    try {
      await api.deleteNode(path);
      await fetchNodes();
      if (activeFileId.value === path) activeFileId.value = null;
    } catch (error) {
      console.error('Failed to delete node:', error);
    }
  };

  const renameNode = async (path: string, newName: string) => {
    // 过滤掉没有变化的重命名
    const oldName = path.split('/').pop();
    if (!newName || newName === oldName) {
        editingNodeId.value = null;
        return;
    }

    try {
      const result = await api.updateNode(path, { name: newName });
      await fetchNodes();

      // 如果重命名的是当前活动文件，更新其 ID
      if (activeFileId.value === path) {
          activeFileId.value = result.path;
      }

      editingNodeId.value = null;
    } catch (error) {
      console.error('Failed to rename node:', error);
      // 可以在这里加个错误提示，或者保持编辑状态
      editingNodeId.value = null;
    }
  };


  const updateContent = async (path: string, content: string) => {
    try {
      console.log('Update content for', path);
    } catch (error) {
      console.error('Failed to update content:', error);
    }
  };

  const fetchFileContent = async (path: string) => {
      try {
          return await api.fileContent(path);
    } catch (error) {
      console.error('Failed to fetch file content:', error);
      return '';
    }
  };

  watch(activeFileId, async(newPath) => {
    if (newPath) {
        activeFileContent.value = await fetchFileContent(newPath);
    } else {
        activeFileContent.value = '';
    }
  });

  const rootNodes = computed(() => [...nodes.value].sort((a, b) => {
    if (a.type !== b.type) return (a.type === 'folder' || a.type === 'directory') ? -1 : 1;
    return a.name.localeCompare(b.name);
  }));

  const moveNode = async (sourcePath: string, targetParentPath: string) => {
    const fileName = sourcePath.split('/').pop();
    const destination = !targetParentPath ? fileName! : `${targetParentPath}/${fileName}`;

    if (sourcePath === destination) return;

    try {
      await api.updateNode(sourcePath, { destination });
      await fetchNodes();
      if (activeFileId.value === sourcePath) {
        activeFileId.value = destination;
      }
    } catch (error) {
      console.error('Failed to move node:', error);
    }
  };

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
    moveNode,
    setEditingNodeId: (id: string | null) => editingNodeId.value = id,
    setActiveFile: (path: string) => activeFileId.value = path,
  };
}
