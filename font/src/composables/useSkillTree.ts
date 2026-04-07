// composables/useSkillTree.ts
import { ref, type Ref } from 'vue'
import request from '../utils/request.js'

type NodeType = 'file' | 'folder'

export interface Node {
  id: string
  name: string
  type: NodeType
  parentId: string | null
  content: string
  createdAt: number
  updatedAt: number
}

interface SkillTreeResponse {
  root_path: string
  children: Array<{
    name: string
    type: 'file' | 'directory'
    path: string
    children?: Array<any>
    content?: string | null
    size?: number
    extension?: string
  }>
  total_files: number
  total_directories: number
}

const INITIAL_NODES: Node[] = [
  {
    id: 'root-folder-1',
    name: 'Getting Started',
    type: 'folder',
    parentId: null,
    content: '',
    createdAt: Date.now(),
    updatedAt: Date.now()
  },
  {
    id: 'welcome-file',
    name: 'Welcome.md',
    type: 'file',
    parentId: 'root-folder-1',
    content: '# Welcome to Markdown Manager\n\nThis is a simple web-based Markdown editor and file manager.\n\n## Features\n\n- **File Tree**: Organize your notes into folders.\n- **Typora-like Editor**: Real-time rendering enabled using Vditor (`ir` mode).\n- **GitHub Flavored Markdown**: supports tables, strikethrough, task lists, and more.\n\n### Code Example\n\n```js\nfunction greet() {\n  console.log("Hello World!");\n}\n```\n\n| Feature | Status |\n| :--- | :--- |\n| Create Files | ✅ |\n| Create Folders | ✅ |\n| Real-time Preview | ✅ |\n| Local State | ✅ |\n\nStart writing by creating a new file or editing this one!',
    createdAt: Date.now(),
    updatedAt: Date.now()
  },
  {
    id: 'root-folder-2',
    name: 'Personal Notes',
    type: 'folder',
    parentId: null,
    content: '',
    createdAt: Date.now(),
    updatedAt: Date.now()
  },
  {
    id: 'todo-file',
    name: 'Tasks.md',
    type: 'file',
    parentId: 'root-folder-2',
    content: '# Tasks\n\n- [x] Integrate Vditor\n- [x] Configure instant rendering (Typora style)\n- [ ] Write more notes\n',
    createdAt: Date.now(),
    updatedAt: Date.now()
  }
]

export function useSkillTree() {
  // ========== State ==========
  const nodes = ref<Node[]>([])
  const isLoading = ref(true)
  const editingNodeId = ref<string | null>(null)
  const editValues = ref<Record<string, string>>({})
  const activeFileId = ref<string | null>(null)

  // ========== Helper Functions ==========
  const generateId = () => Math.random().toString(36).substring(2, 11)

  const convertBackendDataToNodes = (children: any[], parentId: string | null = null): Node[] => {
    const result: Node[] = []
    const now = Date.now()
    
    children.forEach(child => {
      const isFolder = child.type === 'directory'
      const node: Node = {
        id: child.path,
        name: child.name,
        type: isFolder ? 'folder' : 'file',
        parentId: parentId,
        content: child.content || '',
        createdAt: now,
        updatedAt: now
      }
      result.push(node)
      
      if (isFolder && child.children) {
        const childNodes = convertBackendDataToNodes(child.children, child.path)
        result.push(...childNodes)
      }
    })
    
    return result
  }

  const getRootDirectories = (children: any[]): string[] => {
    return children
      .filter(child => child.type === 'directory')
      .map(dir => dir.path)
  }

  const getChildrenIds = (parentId: string): string[] => {
    const children = nodes.value.filter(n => n.parentId === parentId)
    let ids = children.map(c => c.id)
    for (const child of children) {
      if (child.type === 'folder') {
        ids = [...ids, ...getChildrenIds(child.id)]
      }
    }
    return ids
  }

  // ========== Server Operations ==========
  const loadFromServer = async () => {
    try {
      const response = await request.get('/api/skills/tree') as unknown as SkillTreeResponse
      console.log('Loaded skills tree:', response)
      
      const convertedNodes = convertBackendDataToNodes(response.children)
      nodes.value = convertedNodes
      
      return {
        nodes: convertedNodes,
        expandedFolders: getRootDirectories(response.children),
        firstFileId: convertedNodes.find(n => n.type === 'file')?.id || null
      }
    } catch (error) {
      console.error('Failed to load nodes:', error)
      // 确保即使网络请求失败，也能显示初始数据
      nodes.value = INITIAL_NODES
      console.log('Using initial nodes:', INITIAL_NODES)
      return {
        nodes: INITIAL_NODES,
        expandedFolders: ['root-folder-1', 'root-folder-2'],
        firstFileId: 'welcome-file'
      }
    } finally {
      isLoading.value = false
    }
  }

  const loadFileContent = async (fileId: string, fileName: string) => {
    try {
      console.log('Would load file content for:', fileName)
    } catch (error) {
      console.error('Failed to load file content:', error)
    }
  }

  // ========== Business Logic Operations ==========
  
  /**
   * 切换文件夹展开/收起状态
   */
  const toggleFolder = (expandedFolders: Set<string>, folderId: string, forceExpand?: boolean) => {
    console.log('Toggling folder:', folderId)
    if (forceExpand !== undefined) {
      if (forceExpand) {
        expandedFolders.add(folderId)
      } else {
        expandedFolders.delete(folderId)
      }
    } else {
      if (expandedFolders.has(folderId)) {
        expandedFolders.delete(folderId)
      } else {
        expandedFolders.add(folderId)
      }
    }
  }

  /**
   * 创建新节点（文件或文件夹）
   */
  const createNode = (
    type: NodeType, 
    parentId: string | null,
    expandedFolders: Set<string>
  ) => {
    const id = generateId()
    const newNode: Node = {
      id,
      name: type === 'folder' ? 'New Folder' : 'Untitled.md',
      type,
      parentId,
      content: type === 'file' ? '# Untitled\n\n' : '',
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
    
    if (parentId) {
      toggleFolder(expandedFolders, parentId, true)
    }

    nodes.value.push(newNode)
    editingNodeId.value = id
    editValues.value[id] = newNode.name
    
    if (type === 'file') {
      activeFileId.value = id
    }
    
    return newNode
  }

  /**
   * 删除节点及其所有子节点
   */
  const deleteNode = (id: string, expandedFolders: Set<string>) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return
    
    const idsToDelete = [id, ...getChildrenIds(id)]
    nodes.value = nodes.value.filter(n => !idsToDelete.includes(n.id))
    
    if (activeFileId.value && idsToDelete.includes(activeFileId.value)) {
      activeFileId.value = null
    }
  }

  /**
   * 重命名节点
   */
  const renameNode = (nodeId: string, newName: string) => {
    const node = nodes.value.find(n => n.id === nodeId)
    if (node) {
      node.name = newName || (node.type === 'folder' ? 'New Folder' : 'Untitled.md')
      node.updatedAt = Date.now()
    }
    editingNodeId.value = null
  }

  /**
   * 开始编辑模式
   */
  const startEditing = (nodeId: string) => {
    editingNodeId.value = nodeId
    if (!editValues.value[nodeId]) {
      const node = nodes.value.find(n => n.id === nodeId)
      if (node) {
        editValues.value[nodeId] = node.name
      }
    }
  }

  /**
   * 处理编辑时的键盘事件
   */
  const handleEditKeydown = (event: KeyboardEvent, nodeId: string) => {
    if (event.key === 'Enter') {
      renameNode(nodeId, editValues.value[nodeId])
    } else if (event.key === 'Escape') {
      editingNodeId.value = null
      editValues.value[nodeId] = nodes.value.find(n => n.id === nodeId)?.name || ''
    }
  }

  /**
   * 处理编辑框失焦
   */
  const handleEditBlur = (nodeId: string) => {
    renameNode(nodeId, editValues.value[nodeId])
  }

  /**
   * 更新文件内容
   */
  const updateContent = (id: string, content: string) => {
    const node = nodes.value.find(n => n.id === id)
    if (node) {
      node.content = content
      node.updatedAt = Date.now()
    }
  }

  // ========== Return ==========
  return {
    // State
    nodes,
    isLoading,
    editingNodeId,
    editValues,
    activeFileId,
    
    // Server Operations
    loadFromServer,
    loadFileContent,
    
    // Business Logic Operations
    toggleFolder,
    createNode,
    deleteNode,
    renameNode,
    startEditing,
    handleEditKeydown,
    handleEditBlur,
    updateContent
  }
}
