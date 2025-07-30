import { render, screen } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { MemoryRouter } from 'react-router-dom';
import ChatPage from './ChatPage';
import { useChatStore } from '../stores/chatStore';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      <MantineProvider>
        {component}
      </MantineProvider>
    </MemoryRouter>
  );
};

describe('ChatPage', () => {
  beforeEach(() => {
    // 重置 store 狀態
    useChatStore.getState().clearAllSessions();
  });

  test('renders correctly with integrated components', () => {
    renderWithProviders(<ChatPage />);
    
    // 檢查聊天歷史區域
    expect(screen.getByText('聊天歷史')).toBeInTheDocument();
    expect(screen.getByText('尚無聊天記錄')).toBeInTheDocument();
    
    // 檢查歡迎訊息（空狀態）
    expect(screen.getByText('歡迎使用智能助理')).toBeInTheDocument();
    
    // 檢查輸入框
    expect(screen.getByPlaceholderText('請輸入您的訊息...')).toBeInTheDocument();
  });

  test('renders responsive layout with AppShell', () => {
    renderWithProviders(<ChatPage />);
    
    // 檢查 AppShell 結構是否存在
    const navbar = document.querySelector('.mantine-AppShell-navbar');
    const main = document.querySelector('.mantine-AppShell-main');
    
    expect(navbar).toBeInTheDocument();
    expect(main).toBeInTheDocument();
  });

  test('integrates with store correctly for initial state', () => {
    renderWithProviders(<ChatPage />);
    
    const state = useChatStore.getState();
    expect(state.sessions).toEqual([]);
    expect(state.activeSessionId).toBeNull();
    expect(state.messages).toEqual({});
    expect(state.isLoading).toBe(false);
  });

  test('shows new chat button', () => {
    renderWithProviders(<ChatPage />);
    
    const newChatButton = screen.getByTitle('開始新對話');
    expect(newChatButton).toBeInTheDocument();
  });

  test('shows message input component', () => {
    renderWithProviders(<ChatPage />);
    
    expect(screen.getByText('按 Enter 發送，Shift + Enter 換行')).toBeInTheDocument();
    expect(screen.getByTitle('發送訊息 (Enter)')).toBeInTheDocument();
  });
});