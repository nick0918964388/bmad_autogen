import { useState, useRef, KeyboardEvent } from 'react';
import { Box, Textarea, ActionIcon, Group, Paper } from '@mantine/core';
import { IconSend, IconLoader } from '@tabler/icons-react';

interface MessageInputProps {
  onSendMessage?: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  maxRows?: number;
}

export default function MessageInput({
  onSendMessage = () => {},
  isLoading = false,
  disabled = false,
  placeholder = '請輸入您的訊息...',
  maxRows = 6
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !isLoading && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
      
      // 重置 textarea 高度
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter') {
      if (event.shiftKey) {
        // Shift + Enter: 換行
        return;
      } else {
        // Enter: 發送訊息
        event.preventDefault();
        handleSend();
      }
    }
  };

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(event.target.value);
  };

  const canSend = message.trim().length > 0 && !isLoading && !disabled;

  return (
    <Paper 
      p="md" 
      shadow="sm" 
      style={{ 
        borderTop: '1px solid #e9ecef',
        backgroundColor: '#ffffff'
      }}
    >
      <Group gap="md" align="flex-end">
        <Box style={{ flex: 1 }}>
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            autosize
            minRows={1}
            maxRows={maxRows}
            variant="filled"
            radius="lg"
            style={{
              fontSize: '14px',
            }}
            styles={{
              input: {
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                '&:focus': {
                  backgroundColor: '#ffffff',
                  borderColor: '#339af0'
                },
                '&:disabled': {
                  backgroundColor: '#e9ecef',
                  opacity: 0.6
                }
              }
            }}
          />
          
          {/* 使用提示 */}
          <Box mt={4}>
            <Box 
              component="span" 
              style={{ 
                fontSize: '11px', 
                color: '#6c757d' 
              }}
            >
              按 Enter 發送，Shift + Enter 換行
            </Box>
          </Box>
        </Box>

        <ActionIcon
          size="lg"
          radius="lg"
          variant={canSend ? 'filled' : 'light'}
          color={canSend ? 'blue' : 'gray'}
          onClick={handleSend}
          disabled={!canSend}
          style={{
            transition: 'all 0.2s ease',
            transform: canSend ? 'scale(1)' : 'scale(0.95)',
          }}
          title={isLoading ? '發送中...' : '發送訊息 (Enter)'}
        >
          {isLoading ? (
            <IconLoader 
              size={18} 
              style={{ 
                animation: 'spin 1s linear infinite',
              }} 
            />
          ) : (
            <IconSend size={18} />
          )}
        </ActionIcon>
      </Group>
      
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </Paper>
  );
}