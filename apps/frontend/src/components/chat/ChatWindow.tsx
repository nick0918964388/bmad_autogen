import { ScrollArea, Stack, Box, Text, Paper, Avatar, Group } from '@mantine/core';
import { IconUser, IconRobot } from '@tabler/icons-react';
import { useEffect, useRef } from 'react';
import { Message } from '@smart-assistant/shared-types';

interface ChatWindowProps {
  messages: Message[];
  isLoading?: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === 'user';
  const isSystem = message.sender === 'system';

  return (
    <Group gap="md" align="flex-start" style={{ 
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '1rem'
    }}>
      {!isUser && (
        <Avatar color={isSystem ? 'gray' : 'blue'} radius="xl" size="sm">
          <IconRobot size={16} />
        </Avatar>
      )}
      
      <Paper
        p="md"
        radius="lg"
        style={{
          maxWidth: '70%',
          backgroundColor: isUser ? '#007bff' : isSystem ? '#f8f9fa' : '#e9ecef',
          color: isUser ? 'white' : 'black',
          marginLeft: isUser ? 'auto' : 0,
          marginRight: isUser ? 0 : 'auto',
        }}
      >
        <Text size="sm" style={{ wordBreak: 'break-word' }}>
          {message.content}
        </Text>
        <Text size="xs" c={isUser ? 'rgba(255,255,255,0.7)' : 'dimmed'} mt="xs">
          {new Date(message.timestamp).toLocaleString('zh-TW', {
            hour: '2-digit',
            minute: '2-digit',
            month: 'short',
            day: 'numeric'
          })}
        </Text>
      </Paper>

      {isUser && (
        <Avatar color="blue" radius="xl" size="sm">
          <IconUser size={16} />
        </Avatar>
      )}
    </Group>
  );
}

export default function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // 自動滾動到最新訊息
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages]);

  return (
    <ScrollArea 
      h="100%" 
      ref={scrollAreaRef}
      style={{ padding: '1rem' }}
      scrollbarSize={6}
      scrollHideDelay={1000}
    >
      <Stack gap="md">
        {messages.length === 0 ? (
          <Box 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '100%',
              flexDirection: 'column',
              textAlign: 'center',
              color: '#666',
              minHeight: '200px'
            }}
          >
            <IconRobot size={48} stroke={1.5} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <Text size="lg" fw={500} mb="sm">
              歡迎使用智能助理
            </Text>
            <Text size="sm" c="dimmed">
              開始對話，我將協助您解決問題
            </Text>
          </Box>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {/* 載入中指示器 */}
            {isLoading && (
              <Group gap="md" align="flex-start">
                <Avatar color="blue" radius="xl" size="sm">
                  <IconRobot size={16} />
                </Avatar>
                
                <Paper
                  p="md"
                  radius="lg"
                  style={{
                    backgroundColor: '#e9ecef',
                    animation: 'pulse 1.5s ease-in-out infinite',
                  }}
                >
                  <Text size="sm" c="dimmed">
                    正在輸入中...
                  </Text>
                </Paper>
              </Group>
            )}
          </>
        )}
      </Stack>
      
    </ScrollArea>
  );
}