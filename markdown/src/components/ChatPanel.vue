<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { X, Send, User, Bot, Loader2 } from 'lucide-vue-next';
import { api } from '../api/client';

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
}

const emit = defineEmits(['close']);
const message = ref('');
const isLoading = ref(false);
const messages = ref<ChatMessage[]>([
  {
    id: '1',
    content: 'Hello! I am your AI assistant. How can I help you with this document?',
    role: 'assistant',
    timestamp: Date.now()
  }
]);
const chatContainer = ref<HTMLElement | null>(null);

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (message.value.trim() && !isLoading.value) {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: message.value.trim(),
      role: 'user',
      timestamp: Date.now()
    };
    console.log('userMessage:', userMessage)
    messages.value.push(userMessage);
    await scrollToBottom();
    
    const currentMessage = message.value;
    message.value = '';
    isLoading.value = true;
    console.log('currentMessage:', currentMessage)
    try {
      const response = await api.chat(currentMessage);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        role: 'assistant',
        timestamp: Date.now()
      };
      messages.value.push(assistantMessage);
      await scrollToBottom();
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 2).toString(),
        content: 'Sorry, I encountered an error. Please try again later.',
        role: 'assistant',
        timestamp: Date.now()
      };
      messages.value.push(errorMessage);
      await scrollToBottom();
    } finally {
      isLoading.value = false;
    }
  }
};
</script>

<template>
  <div
    class="w-80 md:w-96 border-l border-slate-200 bg-slate-50 flex flex-col shadow-[-4px_0_15px_-3px_rgba(0,0,0,0.05)] transition-all duration-300 animate-in slide-in-from-right"
  >
    <!-- Panel Header -->
    <div class="h-12 px-4 border-b border-slate-200 flex items-center justify-between bg-white shrink-0 shadow-sm z-10">
      <div class="flex items-center gap-2">
        <Bot :size="18" class="text-blue-600" />
        <span class="text-xs font-bold uppercase tracking-wider text-slate-500">AI Assistant</span>
      </div>
      <button @click="emit('close')" class="p-1.5 hover:bg-slate-100 rounded-md text-slate-400 transition-colors">
        <X :size="16" />
      </button>
    </div>

    <!-- Panel Content (Chat History) -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar">
      <!-- Welcome Message -->
      <div v-for="msg in messages" :key="msg.id" :class="{
        'flex items-start gap-2 max-w-[90%]': msg.role === 'assistant',
        'flex items-start gap-2 flex-row-reverse self-end max-w-[90%]': msg.role === 'user'
      }">
        <div :class="{
          'w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 border border-blue-200 shadow-sm': msg.role === 'assistant',
          'w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 border border-slate-200 shadow-sm': msg.role === 'user'
        }">
          <Bot v-if="msg.role === 'assistant'" :size="16" class="text-blue-600" />
          <User v-else :size="16" class="text-slate-600" />
        </div>
        <div :class="{
          'bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 text-sm text-slate-700 shadow-sm leading-relaxed': msg.role === 'assistant',
          'bg-blue-600 p-3 rounded-2xl rounded-tr-none text-sm text-white shadow-sm leading-relaxed': msg.role === 'user'
        }">
          {{ msg.content }}
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex items-start gap-2 max-w-[90%]">
        <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 border border-blue-200 shadow-sm">
          <Loader2 :size="16" class="text-blue-600 animate-spin" />
        </div>
        <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 text-sm text-slate-700 shadow-sm leading-relaxed">
          Thinking...
        </div>
      </div>
    </div>

    <!-- Panel Input -->
    <div class="p-4 border-t border-slate-200 bg-white">
      <div class="relative flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl p-2 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
        <textarea
          v-model="message"
          rows="1"
          placeholder="Ask anything..."
          @keyup.enter.exact.prevent="sendMessage"
          class="flex-1 bg-transparent border-none resize-none py-1 px-1 text-sm focus:ring-0 focus:outline-none min-h-[20px] max-h-32 custom-scrollbar"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!message.trim() || isLoading"
          class="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:bg-slate-300 transition-all shadow-sm shrink-0"
        >
          <Send :size="16" />
        </button>
      </div>
      <p class="text-[10px] text-slate-400 mt-2 text-center">
        AI may produce inaccurate information.
      </p>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation-duration: 0.2s;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-in-from-right {
  animation-name: slideInRight;
}
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

/* 隐藏滚动条但保留功能 */
textarea::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>