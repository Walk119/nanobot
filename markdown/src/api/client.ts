import type { Node } from './types';

// 这里假设您的 API 基础路径，可以根据实际情况在 .env 中配置
const BASE_URL = '/api';

export const api = {
  async getNodes(): Promise<Node[]> {

    const response = await fetch(`${BASE_URL}/skills/tree`);
//     console.log(response.json())
    if (!response.ok) throw new Error('Failed to fetch nodes');
    return response.json();
  },

  async fileContent(file_path): Promise<any>{
      const response = await fetch(`${BASE_URL}/skills/file/raw?file_path=${file_path}`)
//       console.log(response.json())
      if (!response.ok) throw new Error('Failed to fetch file info');
      return response.text();
  },
  async createNode(node: Partial<Node>): Promise<Node> {
    const response = await fetch(`${BASE_URL}/nodes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(node),
    });
    if (!response.ok) throw new Error('Failed to create node');
    return response.json();
  },

  async updateNode(id: string, updates: Partial<Node>): Promise<Node> {
    const response = await fetch(`${BASE_URL}/nodes/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update node');
    return response.json();
  },

  async deleteNode(id: string): Promise<void> {
    const response = await fetch(`${BASE_URL}/nodes/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete node');
  },

  async updateContent(id: string, content: string): Promise<void> {
    const response = await fetch(`${BASE_URL}/nodes/${id}/content`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error('Failed to update content');
  }
};
