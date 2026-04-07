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

export interface ApiClientConfig {
  baseUrl: string;
}
