# React 到 Vue 3 转换说明

本文档说明了将 `markdown` 目录下的 React 代码转换为 `font` 目录下的 Vue 3 代码的详细过程。

## 转换概览

### 原始技术栈 (React)
- React 18 + TypeScript
- Vite (React 插件)
- Tailwind CSS v4
- Vditor (Markdown 编辑器)
- lucide-react (图标库)
- Radix UI 组件库

### 目标技术栈 (Vue 3)
- Vue 3 + TypeScript
- Vite (Vue 插件)
- Tailwind CSS v4
- Vditor (Markdown 编辑器)
- lucide-vue-next (图标库)
- 原生 Vue 组件

## 主要文件和转换要点

### 1. 项目配置文件

#### package.json
**变化：**
- 移除 React 相关依赖 (`react`, `react-dom`)
- 移除 MUI、Radix UI 等 React 组件库
- 添加 Vue 3 依赖
- 添加 `lucide-vue-next` 替代 `lucide-react`
- 添加 `@vitejs/plugin-vue` 替代 `@vitejs/plugin-react`

#### vite.config.ts
**变化：**
```typescript
// React
import react from '@vitejs/plugin-react'
plugins: [react(), tailwindcss()]

// Vue
import vue from '@vitejs/plugin-vue'
plugins: [vue(), tailwindcss()]
```

#### index.html
**变化：**
```html
<!-- React -->
<div id="root"></div>
<script type="module" src="/src/main.tsx"></script>

<!-- Vue -->
<div id="app"></div>
<script type="module" src="/src/main.ts"></script>
```

### 2. 入口文件

#### main.tsx → main.ts
```typescript
// React
import { createRoot } from "react-dom/client"
import App from "./app/App.tsx"
createRoot(document.getElementById("root")!).render(<App />)

// Vue
import { createApp } from 'vue'
import App from './App.vue'
createApp(App).mount('#app')
```

### 3. 核心组件转换

#### App.tsx → App.vue + TreeNode.vue

这是最复杂的转换部分，主要变化包括：

##### 语法差异

**React JSX:**
```tsx
export default function App() {
  const [count, setCount] = useState(0)
  
  return (
    <div className="container">
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  )
}
```

**Vue 3 SFC:**
```vue
<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="container">
    <button @click="count++">Click me</button>
  </div>
</template>
```

##### 状态管理

| React | Vue 3 |
|-------|-------|
| `useState` | `ref` / `reactive` |
| `useEffect` | `onMounted` / `watch` |
| `useRef` | `ref` / Template refs |
| `useMemo` | `computed` |
| `useCallback` | Methods in `<script>` |

##### 事件处理

| React | Vue 3 |
|-------|-------|
| `onClick={handler}` | `@click="handler"` |
| `onChange={handler}` | `@change="handler"` |
| `onKeyDown={handler}` | `@keydown="handler"` |
| `e.stopPropagation()` | `$event.stopPropagation()` or `.stop` modifier |

##### 条件渲染

**React:**
```tsx
{isLoading && <LoadingSpinner />}
{items.length > 0 ? (
  <List items={items} />
) : (
  <EmptyState />
)}
```

**Vue:**
```vue
<LoadingSpinner v-if="isLoading" />
<List v-if="items.length > 0" :items="items" />
<EmptyState v-else />
```

##### 列表渲染

**React:**
```tsx
{items.map(item => (
  <ListItem key={item.id} item={item} />
))}
```

**Vue:**
```vue
<ListItem 
  v-for="item in items" 
  :key="item.id" 
  :item="item" 
/>
```

##### 组件通信

**Props (Parent to Child):**

React:
```tsx
<Child name="John" age={25} />
```

Vue:
```vue
<Child :name="'John'" :age="25" />
<!-- or -->
<Child name="John" :age="25" />
```

**Events (Child to Parent):**

React:
```tsx
// Parent
<Child onAction={(data) => handleAction(data)} />

// Child
props.onAction(data)
```

Vue:
```vue
<!-- Parent -->
<Child @action="handleAction" />

<!-- Child -->
emit('action', data)
```

### 4. 递归组件处理

在 React 版本中，`TreeNode` 组件使用函数式组件和 JSX 实现递归。在 Vue 中，我们创建了一个单独的 `.vue` 文件，并通过组件名称引用自身：

```vue
<!-- TreeNode.vue -->
<script setup>
// 组件逻辑
</script>

<template>
  <div>
    <!-- 递归调用自身 -->
    <TreeNode 
      v-if="hasChildren" 
      v-for="child in children" 
      :node="child" 
    />
  </div>
</template>
```

### 5. 样式处理

所有样式都保持不变，因为两个版本都使用 Tailwind CSS。主要的样式类完全一致：

- Flexbox 布局
- Spacing (padding, margin)
- Colors
- Typography
- Transitions
- Custom scrollbar styles

Vditor 编辑器的样式也保持一致，使用 `:deep()` 选择器来覆盖第三方库的样式。

## 功能特性保留

转换后的 Vue 版本完整保留了以下功能：

✅ 文件树结构管理
✅ 创建文件/文件夹
✅ 重命名功能
✅ 删除功能（含确认）
✅ 文件夹展开/折叠
✅ Vditor Markdown 编辑器
✅ 即时渲染模式 (Typora 风格)
✅ 大纲视图
✅ 响应式布局
✅ 悬停效果
✅ 编辑状态高亮

## 代码结构对比

### React 版本
```
markdown/
├── src/
│   ├── app/
│   │   └── App.tsx (包含 TreeNode 组件)
│   ├── main.tsx
│   └── styles/
└── ...
```

### Vue 版本
```
font/
├── src/
│   ├── App.vue (主应用组件)
│   ├── TreeNode.vue (独立的树节点组件)
│   ├── main.ts
│   └── styles/
└── ...
```

## 性能优化

Vue 版本继承了 React 版本的性能特点：
- 使用 `computed` 缓存计算属性
- 使用 `v-if` 进行条件渲染
- 使用 `v-for` with `key` 优化列表渲染
- 使用 `nextTick` 处理 DOM 更新时机

## 运行步骤

### 安装依赖
```bash
cd font
npm install
```

### 开发模式
```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本
```bash
npm run build
```

## 注意事项

1. **JSX vs Template**: Vue 版本使用了更标准的模板语法而非 JSX，使代码更易读易维护

2. **双向绑定**: 使用 `v-model` 或 `:value` + `@input` 实现表单绑定

3. **生命周期**: 
   - `onMounted` ≈ `useEffect(..., [])`
   - `onUnmounted` ≈ cleanup function in `useEffect`

4. **类型支持**: 两个版本都完全支持 TypeScript

5. **图标库**: 从 `lucide-react` 切换到 `lucide-vue-next`，API 略有不同：
   ```tsx
   // React
   <FileText size={16} className="text-blue-500" />
   
   // Vue
   <FileText :size="16" class="text-blue-500" />
   ```

## 总结

这次转换成功地将 React 应用迁移到 Vue 3，同时：
- ✅ 保持所有功能不变
- ✅ 保持样式完全一致
- ✅ 使用 Vue 3 最佳实践
- ✅ 代码结构更清晰（分离 TreeNode 组件）
- ✅ 完整的 TypeScript 支持
- ✅ 相同的构建工具和依赖管理

转换过程中遵循了 Vue 3 的组合式 API (Composition API) 模式，使代码更加模块化和可维护。
