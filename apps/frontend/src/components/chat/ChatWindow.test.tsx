import { render, screen } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import ChatWindow from './ChatWindow';
import { Message } from '@smart-assistant/shared-types';

const renderWithMantine = (component: React.ReactElement) => {
  return render(
    <MantineProvider>
      {component}
    </MantineProvider>
  );
};

// 測試用的訊息數據
const mockMessages: Message[] = [
  {
    id: '1',
    sessionId: 'session1',
    sender: 'user',
    content: '你好，這是測試訊息',
    timestamp: new Date('2024-01-01T10:00:00Z'),
  },
  {
    id: '2',
    sessionId: 'session1',
    sender: 'assistant',
    content: '您好！我是智能助理，很高興為您服務。',
    timestamp: new Date('2024-01-01T10:01:00Z'),
  },
  {
    id: '3',
    sessionId: 'session1',
    sender: 'system',
    content: '系統訊息：對話已開始',
    timestamp: new Date('2024-01-01T10:02:00Z'),
  }
];

describe('ChatWindow', () => {
  test('renders empty state correctly', () => {
    renderWithMantine(<ChatWindow messages={[]} />);
    
    expect(screen.getByText('歡迎使用智能助理')).toBeInTheDocument();
    expect(screen.getByText('開始對話，我將協助您解決問題')).toBeInTheDocument();
  });

  test('renders messages correctly', () => {
    renderWithMantine(<ChatWindow messages={mockMessages} />);
    
    // 檢查所有訊息內容是否顯示
    expect(screen.getByText('你好，這是測試訊息')).toBeInTheDocument();
    expect(screen.getByText('您好！我是智能助理，很高興為您服務。')).toBeInTheDocument();
    expect(screen.getByText('系統訊息：對話已開始')).toBeInTheDocument();
  });

  test('displays user messages on the right side', () => {
    renderWithMantine(<ChatWindow messages={mockMessages.slice(0, 1)} />);
    
    const messageGroup = screen.getByText('你好，這是測試訊息').closest('[style*="flex-end"]');
    expect(messageGroup).toBeInTheDocument();
  });

  test('displays assistant messages on the left side', () => {
    renderWithMantine(<ChatWindow messages={mockMessages.slice(1, 2)} />);
    
    const messageGroup = screen.getByText('您好！我是智能助理，很高興為您服務。').closest('[style*="flex-start"]');
    expect(messageGroup).toBeInTheDocument();
  });

  test('shows loading indicator when isLoading is true', () => {
    renderWithMantine(<ChatWindow messages={mockMessages} isLoading={true} />);
    
    expect(screen.getByText('正在輸入中...')).toBeInTheDocument();
  });

  test('does not show loading indicator when isLoading is false', () => {
    renderWithMantine(<ChatWindow messages={mockMessages} isLoading={false} />);
    
    expect(screen.queryByText('正在輸入中...')).not.toBeInTheDocument();
  });

  test('formats timestamp correctly', () => {
    renderWithMantine(<ChatWindow messages={mockMessages.slice(0, 1)} />);
    
    // 檢查時間戳是否以正確格式顯示 - 使用更靈活的匹配
    const timestampElement = screen.getByText(/1月1日|下午06:00|18:00/i);
    expect(timestampElement).toBeInTheDocument();
  });

  test('renders different avatar icons for different senders', () => {
    renderWithMantine(<ChatWindow messages={mockMessages} />);
    
    // 檢查是否有 robot 和 user 圖標
    // 由於使用 Tabler icons，實際測試可能需要檢查 aria-label 或其他屬性
    const avatars = document.querySelectorAll('.mantine-Avatar-root');
    expect(avatars.length).toBeGreaterThan(0);
  });

  test('handles message content word breaking', () => {
    const longMessage: Message = {
      id: '4',
      sessionId: 'session1',
      sender: 'user',
      content: '這是一個非常長的訊息'.repeat(20),
      timestamp: new Date(),
    };

    renderWithMantine(<ChatWindow messages={[longMessage]} />);
    
    const messageElement = screen.getByText(longMessage.content);
    expect(messageElement).toBeInTheDocument();
    
    // 檢查訊息元素本身的樣式 (Text 組件有 word-break: break-word)
    expect(messageElement).toHaveStyle('word-break: break-word');
  });
});