export type NodeType = 'file' | 'folder';

export interface Node {
  id: string;
  name: string;
  type: NodeType;
  parentId: string | null;
  content?: string;
  createdAt?: number;
  updatedAt?: number;
  children?: Node[];
}

export interface Project {
  name: string;
  path: string;
  description: string;
  created_at?: string;
}

export interface ProjectsResponse {
  projects: Project[];
}

export interface ApiClientConfig {
  baseUrl: string;
}
