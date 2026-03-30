import React, { useState, useEffect, useRef, KeyboardEvent } from 'react';
import Vditor from 'vditor';
import 'vditor/dist/index.css';
import { 
  Folder, FolderOpen, FileText, FilePlus, FolderPlus, 
  Trash2, Edit2, ChevronRight, ChevronDown, PanelLeftClose, 
  PanelLeft, FileBox, Plus
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type NodeType = 'file' | 'folder';

interface Node {
  id: string;
  name: string;
  type: NodeType;
  parentId: string | null;
  content: string;
  createdAt: number;
  updatedAt: number;
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
];

const generateId = () => Math.random().toString(36).substring(2, 11);

export default function App() {
  const [nodes, setNodes] = useState<Node[]>(INITIAL_NODES);
  const [activeFileId, setActiveFileId] = useState<string | null>('welcome-file');
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['root-folder-1', 'root-folder-2']));
  const [editingNodeId, setEditingNodeId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Vditor setup
  const vditorRef = useRef<HTMLDivElement>(null);
  const vditorInstance = useRef<Vditor | null>(null);

  // Derived state
  const activeFile = nodes.find(n => n.id === activeFileId && n.type === 'file');

  useEffect(() => {
    if (!vditorRef.current || !activeFile) return;

    // Initialize Vditor only when activeFileId changes
    const initVditor = () => {
      vditorInstance.current = new Vditor(vditorRef.current!, {
        height: '100%',
        mode: 'ir', // Instant Rendering (Typora-like style)
        cache: { enable: false }, // We handle our own state via `nodes`
        value: activeFile.content,
        outline: {
          enable: true,
          position: 'right',
        },
        toolbarConfig: {
          pin: true,
        },
        input: (value) => {
          updateContent(activeFile.id, value);
        },
      });
    };

    initVditor();

    return () => {
      if (vditorInstance.current) {
        vditorInstance.current.destroy();
        vditorInstance.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFileId]); // Only recreate when switching files

  // Actions
  const toggleFolder = (folderId: string, forceExpand?: boolean) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(folderId) && !forceExpand) {
        next.delete(folderId);
      } else {
        next.add(folderId);
      }
      return next;
    });
  };

  const createNode = (type: NodeType, parentId: string | null = null, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    
    const id = generateId();
    const newNode: Node = {
      id,
      name: type === 'folder' ? 'New Folder' : 'Untitled.md',
      type,
      parentId,
      content: type === 'file' ? '# Untitled\n\n' : '',
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
    
    if (parentId) {
      toggleFolder(parentId, true);
    }

    setNodes(prev => [...prev, newNode]);
    setEditingNodeId(id);
    if (type === 'file') {
      setActiveFileId(id);
    }
  };

  const getChildrenIds = (parentId: string, allNodes: Node[]): string[] => {
    const children = allNodes.filter(n => n.parentId === parentId);
    let ids = children.map(c => c.id);
    for (const child of children) {
      if (child.type === 'folder') {
        ids = [...ids, ...getChildrenIds(child.id, allNodes)];
      }
    }
    return ids;
  };

  const deleteNode = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    const idsToDelete = [id, ...getChildrenIds(id, nodes)];
    setNodes(prev => prev.filter(n => !idsToDelete.includes(n.id)));
    if (activeFileId && idsToDelete.includes(activeFileId)) {
      setActiveFileId(null);
    }
  };

  const renameNode = (id: string, newName: string) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, name: newName || (n.type === 'folder' ? 'New Folder' : 'Untitled.md') } : n));
    setEditingNodeId(null);
  };

  const updateContent = (id: string, content: string) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, content, updatedAt: Date.now() } : n));
  };

  // Tree Node Component
  const TreeNode = ({ node, depth }: { node: Node; depth: number }) => {
    const isExpanded = expandedFolders.has(node.id);
    const isEditing = editingNodeId === node.id;
    const isActive = activeFileId === node.id;
    const isFolder = node.type === 'folder';

    const [editValue, setEditValue] = useState(node.name);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
      if (isEditing && inputRef.current) {
        inputRef.current.focus();
        inputRef.current.select();
      }
    }, [isEditing]);

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        renameNode(node.id, editValue);
      } else if (e.key === 'Escape') {
        setEditingNodeId(null);
        setEditValue(node.name);
      }
    };

    const handleBlur = () => {
      renameNode(node.id, editValue);
    };

    return (
      <div className="select-none">
        <div 
          className={cn(
            "group flex items-center py-1.5 px-2 cursor-pointer text-sm transition-colors",
            isActive ? "bg-blue-50 text-blue-700" : "text-slate-700 hover:bg-slate-100/80",
            isEditing && "bg-slate-100"
          )}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          onClick={() => {
            if (isFolder) {
              toggleFolder(node.id);
            } else {
              setActiveFileId(node.id);
            }
          }}
        >
          {/* Node Icon */}
          <div className="w-5 flex items-center justify-center mr-1.5 shrink-0">
            {isFolder ? (
              isExpanded ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />
            ) : (
              <FileText size={14} className={isActive ? "text-blue-500" : "text-slate-400"} />
            )}
          </div>
          
          {isFolder && (
            <div className="mr-1.5 shrink-0">
              {isExpanded ? <FolderOpen size={14} className="text-blue-500" /> : <Folder size={14} className="text-blue-500" />}
            </div>
          )}

          {/* Node Label / Input */}
          <div className="flex-1 truncate min-w-0">
            {isEditing ? (
              <input
                ref={inputRef}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
                className="w-full bg-white border border-blue-400 rounded px-1 text-sm outline-none"
                onClick={e => e.stopPropagation()}
              />
            ) : (
              <span className={cn("truncate block", isActive && "font-medium")}>
                {node.name}
              </span>
            )}
          </div>

          {/* Hover Actions */}
          {!isEditing && (
            <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 shrink-0 ml-2">
              {isFolder && (
                <>
                  <button onClick={(e) => createNode('file', node.id, e)} className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded" title="New File">
                    <FilePlus size={12} />
                  </button>
                  <button onClick={(e) => createNode('folder', node.id, e)} className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded" title="New Folder">
                    <FolderPlus size={12} />
                  </button>
                </>
              )}
              <button 
                onClick={(e) => { e.stopPropagation(); setEditingNodeId(node.id); }} 
                className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded" 
                title="Rename"
              >
                <Edit2 size={12} />
              </button>
              <button 
                onClick={(e) => deleteNode(node.id, e)} 
                className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded" 
                title="Delete"
              >
                <Trash2 size={12} />
              </button>
            </div>
          )}
        </div>

        {/* Render Children if Expanded Folder */}
        {isFolder && isExpanded && (
          <div className="flex flex-col">
            {nodes
              .filter(n => n.parentId === node.id)
              .sort((a, b) => {
                if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
                return a.name.localeCompare(b.name);
              })
              .map(child => (
                <TreeNode key={child.id} node={child} depth={depth + 1} />
              ))}
          </div>
        )}
      </div>
    );
  };

  // Render root nodes
  const rootNodes = nodes
    .filter(n => n.parentId === null)
    .sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden font-sans">
      
      {/* Sidebar */}
      {isSidebarOpen && (
        <div className="w-64 md:w-72 flex-shrink-0 border-r border-slate-200 bg-slate-50/80 flex flex-col backdrop-blur-sm shadow-sm z-10">
          <div className="h-12 border-b border-slate-200 flex items-center justify-between px-4 shrink-0 bg-slate-100/50">
            <div className="flex items-center gap-2">
              <FileBox size={18} className="text-blue-600" />
              <span className="font-semibold text-sm tracking-wide text-slate-800 uppercase">Explorer</span>
            </div>
            <div className="flex gap-1.5">
              <button 
                onClick={(e) => createNode('file', null, e)} 
                className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors"
                title="New Root File"
              >
                <FilePlus size={16} />
              </button>
              <button 
                onClick={(e) => createNode('folder', null, e)} 
                className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-md transition-colors"
                title="New Root Folder"
              >
                <FolderPlus size={16} />
              </button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto py-2 px-1 custom-scrollbar">
            {rootNodes.map(node => (
              <TreeNode key={node.id} node={node} depth={0} />
            ))}
            {rootNodes.length === 0 && (
               <div className="text-center p-4 text-sm text-slate-500 mt-4">
                 No files yet. Create one to get started!
               </div>
            )}
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        
        {/* Top Header */}
        <div className="h-12 border-b border-slate-200 bg-white flex items-center px-4 justify-between shrink-0 shadow-sm z-10 relative">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
              className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors"
              title="Toggle Sidebar"
            >
              {isSidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
            </button>
            
            {activeFile && (
              <div className="flex items-center gap-2 px-2 py-1 bg-blue-50/50 rounded-md border border-blue-100">
                <FileText size={16} className="text-blue-500" />
                <span className="text-sm font-medium text-slate-700">
                  {activeFile.name}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Editor Area (Vditor) */}
        {activeFile ? (
          <div className="flex-1 flex overflow-hidden">
            <div className="w-full h-full relative vditor-container">
              <div ref={vditorRef} className="absolute inset-0 border-none" />
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="flex-1 flex items-center justify-center bg-slate-50/50 text-slate-400">
            <div className="text-center max-w-sm px-6">
              <div className="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm border border-slate-200">
                <FileBox size={40} className="text-slate-300" />
              </div>
              <h3 className="text-xl font-medium text-slate-700 mb-2">No File Selected</h3>
              <p className="text-slate-500 mb-6 text-sm leading-relaxed">
                Select a markdown file from the sidebar to start writing, or create a new file to capture your thoughts.
              </p>
              <button 
                onClick={(e) => createNode('file', null, e)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm inline-flex items-center gap-2"
              >
                <Plus size={16} />
                Create New File
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent; 
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1; 
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8; 
        }

        /* Vditor overrides to match the design */
        .vditor-container .vditor {
          border: none !important;
          border-radius: 0;
        }
        .vditor-container .vditor-toolbar {
          border-bottom: 1px solid #e2e8f0 !important;
          background-color: #f8fafc !important;
          padding: 8px 16px !important;
        }
        .vditor-container .vditor-outline {
          border-left: 1px solid #e2e8f0 !important;
          background-color: #f8fafc !important;
        }
        .vditor-container .vditor-ir {
          padding: 24px 48px !important;
          font-family: inherit !important;
        }
        .vditor-container .vditor-reset {
          font-family: inherit !important;
          color: #334155 !important;
        }
      `}</style>
    </div>
  );
}
