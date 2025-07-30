import { render, screen, fireEvent } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import MessageInput from './MessageInput';

const renderWithMantine = (component: React.ReactElement) => {
  return render(
    <MantineProvider>
      {component}
    </MantineProvider>
  );
};

describe('MessageInput', () => {
  test('renders correctly with default props', () => {
    renderWithMantine(<MessageInput />);
    
    expect(screen.getByPlaceholderText('請輸入您的訊息...')).toBeInTheDocument();
    expect(screen.getByText('按 Enter 發送，Shift + Enter 換行')).toBeInTheDocument();
    expect(screen.getByTitle('發送訊息 (Enter)')).toBeInTheDocument();
  });

  test('renders with custom placeholder', () => {
    renderWithMantine(<MessageInput placeholder="自訂提示文字" />);
    
    expect(screen.getByPlaceholderText('自訂提示文字')).toBeInTheDocument();
  });

  test('handles text input correctly', () => {
    renderWithMantine(<MessageInput />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...') as HTMLTextAreaElement;
    
    fireEvent.change(textarea, { target: { value: '測試訊息' } });
    expect(textarea.value).toBe('測試訊息');
  });

  test('calls onSendMessage when send button is clicked', () => {
    const mockOnSendMessage = jest.fn();
    renderWithMantine(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    const sendButton = screen.getByTitle('發送訊息 (Enter)');
    
    fireEvent.change(textarea, { target: { value: '測試訊息' } });
    fireEvent.click(sendButton);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('測試訊息');
  });

  test('calls onSendMessage when Enter is pressed', () => {
    const mockOnSendMessage = jest.fn();
    renderWithMantine(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    
    fireEvent.change(textarea, { target: { value: '測試訊息' } });
    fireEvent.keyDown(textarea, { key: 'Enter' });
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('測試訊息');
  });

  test('does not send message when Shift+Enter is pressed', () => {
    const mockOnSendMessage = jest.fn();
    renderWithMantine(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    
    fireEvent.change(textarea, { target: { value: '測試訊息' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });
    
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('clears input after sending message', () => {
    const mockOnSendMessage = jest.fn();
    renderWithMantine(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...') as HTMLTextAreaElement;
    const sendButton = screen.getByTitle('發送訊息 (Enter)');
    
    fireEvent.change(textarea, { target: { value: '測試訊息' } });
    fireEvent.click(sendButton);
    
    expect(textarea.value).toBe('');
  });

  test('does not send empty or whitespace-only messages', () => {
    const mockOnSendMessage = jest.fn();
    renderWithMantine(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    const sendButton = screen.getByTitle('發送訊息 (Enter)');
    
    // 測試空字串
    fireEvent.change(textarea, { target: { value: '' } });
    fireEvent.click(sendButton);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
    
    // 測試純空白字串
    fireEvent.change(textarea, { target: { value: '   ' } });
    fireEvent.click(sendButton);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('trims whitespace from messages before sending', () => {
    const mockOnSendMessage = jest.fn();
    renderWithMantine(<MessageInput onSendMessage={mockOnSendMessage} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    const sendButton = screen.getByTitle('發送訊息 (Enter)');
    
    fireEvent.change(textarea, { target: { value: '  測試訊息  ' } });
    fireEvent.click(sendButton);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('測試訊息');
  });

  test('disables input and button when isLoading is true', () => {
    renderWithMantine(<MessageInput isLoading={true} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    const sendButton = screen.getByTitle('發送中...');
    
    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  test('disables input and button when disabled is true', () => {
    renderWithMantine(<MessageInput disabled={true} />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    
    expect(textarea).toBeDisabled();
  });

  test('shows loading icon when isLoading is true', () => {
    renderWithMantine(<MessageInput isLoading={true} />);
    
    // 檢查是否有載入圖標 (IconLoader)
    const loadingIcon = document.querySelector('svg');
    expect(loadingIcon).toBeInTheDocument();
    expect(screen.getByTitle('發送中...')).toBeInTheDocument();
  });

  test('shows send icon when not loading', () => {
    renderWithMantine(<MessageInput />);
    
    // 檢查是否有發送圖標 (IconSend)
    const sendIcon = document.querySelector('svg');
    expect(sendIcon).toBeInTheDocument();
    expect(screen.getByTitle('發送訊息 (Enter)')).toBeInTheDocument();
  });

  test('button appearance changes based on message content', () => {
    renderWithMantine(<MessageInput />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    const sendButton = screen.getByTitle('發送訊息 (Enter)');
    
    // 初始狀態 - 按鈕應該是灰色/不可用樣式
    expect(sendButton).toBeDisabled();
    
    // 輸入文字後 - 按鈕應該變為可用
    fireEvent.change(textarea, { target: { value: '測試' } });
    expect(sendButton).not.toBeDisabled();
  });

  test('handles multiline input correctly', () => {
    renderWithMantine(<MessageInput />);
    
    const textarea = screen.getByPlaceholderText('請輸入您的訊息...');
    
    fireEvent.change(textarea, { target: { value: '第一行\n第二行' } });
    expect((textarea as HTMLTextAreaElement).value).toBe('第一行\n第二行');
  });
});