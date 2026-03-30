// composables/useSkillTree.ts
import { ref } from 'vue'
import request from '../utils/request.js'

type NodeType = 'file' | 'folder'

interface Node {
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
    content: '# Welcome to Markdown Manager\n\nThis is a simple web-based Markdown editor and file manager.\n\n## Features\n\n- **File Tree**: Organize your notes into folders.\n- **Typora-like Editor**: Real-time rendering enabled using Vditor (`ir` mode).\n- **GitHub Flavored Markdown**: Supports tables, strikethrough, task lists, and more.\n\n### Code Example\n\n```js\nfunction greet() {\n  console.log("Hello World!");\n}\n```\n\n| Feature | Status |\n| :--- | :--- |\n| Create Files | ✅ |\n| Create Folders | ✅ |\n| Real-time Preview | ✅ |\n| Local State | ✅ |\n\nStart writing by creating a new file or editing this one!',
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
  const nodes = ref<Node[]>([])
  const isLoading = ref(true)

  // 将后端数据转换为 Node 格式
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
      
      // 递归处理子目录
      if (isFolder && child.children) {
        const childNodes = convertBackendDataToNodes(child.children, child.path)
        result.push(...childNodes)
      }
    })
    
    return result
  }

  // 从后端加载节点数据
  const loadFromServer = async () => {
    try {
      const response = await request.get('/api/skills/tree') as unknown as SkillTreeResponse
      console.log('Loaded skills tree:', response)
      
      // 转换后端数据为 Node 格式
      const convertedNodes = convertBackendDataToNodes(response.children)
      nodes.value = convertedNodes
      
      return {
        nodes: convertedNodes,
        expandedFolders: getRootDirectories(response.children),
        firstFileId: convertedNodes.find(n => n.type === 'file')?.id || null
      }
    } catch (error) {
      console.error('Failed to load nodes:', error)
      // 加载失败时使用本地默认数据
      nodes.value = INITIAL_NODES
      return {
        nodes: INITIAL_NODES,
        expandedFolders: ['root-folder-1', 'root-folder-2'],
        firstFileId: 'welcome-file'
      }
    } finally {
      isLoading.value = false
    }
  }

  // 获取所有根目录（用于默认展开）
  const getRootDirectories = (children: any[]): string[] => {
    return children
      .filter(child => child.type === 'directory')
      .map(dir => dir.path)
  }

  // 加载文件内容
  const loadFileContent = async (fileId: string, fileName: string) => {
    try {
      // TODO: 根据实际 API 调整，这里假设有一个获取文件详情的接口
      // const response = await request.get(`/api/skills/file/${fileId}`)
      // const fileNode = nodes.value.find(n => n.id === fileId)
      // if (fileNode) {
      //   fileNode.content = response.content || ''
      // }
      console.log('Would load file content for:', fileName)
    } catch (error) {
      console.error('Failed to load file content:', error)
    }
  }

  return {
    nodes,
    isLoading,
    loadFromServer,
    loadFileContent
  }
}
