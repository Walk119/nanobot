import type { Node } from './types';
import {skillRoot} from '../store/settings'
const BASE_URL = '/api';
// let skillRoot = '';

/**
 * 辅助函数：构建带查询参数的 URL，自动包含 skill_root
 */
const getUrl = (path: string, params: Record<string, string> = {}) => {
  // 使用当前 origin 构造 URL 对象
  const url = new URL(window.location.origin + BASE_URL + path);
   console.log(url)
   console.log(skillRoot.value)
  // 始终尝试添加 skill_root 参数
  if (skillRoot) {
    url.searchParams.append('skill_root', skillRoot.value);
  }
    console.log(url.toString())

  // 添加传入的额外参数
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, value);
    }
  });

  return url.toString();
};

export const api = {
  /**
   * 设置全局使用的 skill_root 路径
   */


  async getNodes(): Promise<Node[]> {
    const response = await fetch(getUrl('/skills/tree'));
    if (!response.ok) throw new Error('Failed to fetch nodes');
    return response.json();
  },

  async fileContent(file_path: string): Promise<string> {
    const response = await fetch(getUrl('/skills/file/raw', { file_path }));
    if (!response.ok) throw new Error('Failed to fetch file info');
    return response.text();
  },

  async createNode(node: Partial<Node>): Promise<Node> {
    const response = await fetch(getUrl('/nodes'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(node),
    });
    if (!response.ok) throw new Error('Failed to create node');
    return response.json();
  },

  async updateNode(id: string, updates: Partial<Node>): Promise<Node> {
    const response = await fetch(getUrl(`/nodes/${id}`), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update node');
    return response.json();
  },

  async deleteNode(id: string): Promise<void> {
    const response = await fetch(getUrl(`/nodes/${id}`), {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete node');
  },

  async updateContent(id: string, content: string): Promise<void> {
    const response = await fetch(getUrl(`/nodes/${id}/content`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error('Failed to update content');
  }
};
