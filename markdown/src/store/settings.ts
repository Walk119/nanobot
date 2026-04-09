import { ref } from 'vue';

// 集中管理 skillRoot
export const skillRoot = ref('nanobot/skills');

// 也可以提供一个更新函数，方便日志追踪或逻辑扩展
export const updateSkillRoot = (newPath: string) => {
  console.log(`Setting skill root to: ${newPath}`);
  skillRoot.value = newPath;
};