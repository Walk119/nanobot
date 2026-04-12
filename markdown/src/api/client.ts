import type { Node, Project, ProjectsResponse } from './types';
import { skillRoot } from '../store/settings'
const BASE_URL = '/api';

/**
 * 辅助函数：构建带查询参数的 URL，自动包含 skill_root
 */
const getUrl = (path: string, params: Record<string, string | undefined> = {}) => {
  const url = new URL(window.location.origin + BASE_URL + path);

  // 始终尝试添加 skill_root 参数
  if (skillRoot) {
    url.searchParams.append('skill_root', skillRoot.value);
  }

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
   * 技能与节点相关接口
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

  async saveFileContent(file_path: string, content: string): Promise<void> {
    const response = await fetch(getUrl('/skills/file/raw', { file_path }), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error('Failed to save file content');
  },

  /**
   * 项目管理接口 (基于 path)
   */
  async listProjects(): Promise<ProjectsResponse> {
    const response = await fetch(getUrl('/projects'));
    if (!response.ok) throw new Error('Failed to fetch projects');
    return response.json();
  },

  async getProjectDetail(path: string): Promise<Project> {
    const response = await fetch(getUrl('/projects/detail', { path }));
    if (!response.ok) throw new Error('Failed to fetch project detail');
    return response.json();
  },

  async registerProject(project: { path: string; name?: string; description?: string }): Promise<Project> {
    const response = await fetch(getUrl('/projects'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project),
    });
    if (!response.ok) throw new Error('Failed to register project');
    return response.json();
  },

  async updateProject(path: string, updates: { name?: string; description?: string }): Promise<Project> {
    const response = await fetch(getUrl('/projects', { path }), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update project');
    return response.json();
  },

  async unregisterProject(path: string): Promise<void> {
    const response = await fetch(getUrl('/projects', { path }), {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to unregister project');
  },

  async createNode(node: { name: string; type: string; parentId: string | null; content?: string }): Promise<Node> {
    const response = await fetch(getUrl('/nodes'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(node),
    });
    return response.json();
  },

  async updateNode(path: string, updates: { name?: string; destination?: string; content?: string }): Promise<any> {
    const response = await fetch(getUrl(`/nodes/${path}`), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  },

  async deleteNode(path: string): Promise<void> {
    const response = await fetch(getUrl(`/nodes/${path}`), {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete node');
  },

  async chat(message: string, session_id?: string): Promise<{ content: string; metadata?: any }> {
    const response = await fetch('http://127.0.0.1:8000/api/skills/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id }),
    });
    if (!response.ok) throw new Error('Failed to send chat message');
    return response.json();
  }
};
