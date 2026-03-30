# Markdown Manager - Vue 3 Version

这是一个从 React 转换过来的 Markdown 编辑器和管理器应用，使用 Vue 3 + TypeScript + Vite 构建。

## 功能特性

- 📁 **文件树管理**: 支持创建文件夹和文件，组织你的笔记
- ✏️ **Typora 风格编辑器**: 使用 Vditor 实现即时渲染
- 🎨 **GitHub Flavored Markdown**: 支持表格、删除线、任务列表等
- 🔄 **实时预览**: 编辑时即时看到渲染效果
- 💾 **本地状态管理**: 所有数据保存在内存中

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - JavaScript 的超集
- **Vite** - 下一代前端构建工具
- **Tailwind CSS v4** - 实用优先的 CSS 框架
- **Vditor** - 浏览器端的 Markdown 编辑器
- **Lucide Vue Next** - 图标库

## 安装和运行

### 1. 安装依赖

```bash
cd font
npm install
```

### 2. 开发模式

```bash
npm run dev
```

启动后，访问 http://localhost:5173 查看应用

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
font/
├── src/
│   ├── App.vue          # 主应用组件
│   ├── main.ts          # 应用入口
│   └── styles/          # 样式文件
│       ├── index.css    # 样式入口
│       ├── fonts.css    # 字体导入
│       ├── tailwind.css # Tailwind 配置
│       └── theme.css    # 主题变量
├── index.html           # HTML 模板
├── package.json         # 项目依赖
└── vite.config.ts       # Vite 配置
```

## 主要功能说明

### 文件操作
- **创建文件/文件夹**: 点击侧边栏顶部的 `+` 按钮
- **重命名**: 点击文件或文件夹右侧的重命名图标
- **删除**: 点击删除图标可删除文件或文件夹（会确认）
- **展开/折叠**: 点击文件夹可展开或折叠

### 编辑器功能
- 支持 Markdown 所有语法
- 支持代码高亮
- 支持表格渲染
- 支持任务列表
- 大纲视图（右侧）

## 注意事项

1. 当前版本数据存储在内存中，刷新页面会丢失数据
2. 如需持久化存储，可以添加 localStorage 或后端 API
3. 样式已尽可能还原 React 版本

## 与 React 版本的对比

| 特性 | React 版本 | Vue 版本 |
|------|-----------|---------|
| 框架 | React 18 | Vue 3 |
| 状态管理 | Hooks | Composition API |
| 图标 | lucide-react | lucide-vue-next |
| 构建工具 | Vite + React 插件 | Vite + Vue 插件 |
| 组件写法 | JSX | Template + JSX |

## 开发说明

### 添加新功能
可以在 `App.vue` 中的 script setup 部分添加新的功能和逻辑

### 修改样式
- 全局样式：修改 `src/styles` 下的 CSS 文件
- 组件样式：在 `<style scoped>` 中添加

### 自定义主题
修改 `theme.css` 中的 CSS 变量来自定义主题颜色

## License

MIT
