import { Stack, Box, Text, Paper, Group, ActionIcon, UnstyledButton, ScrollArea } from '@mantine/core';
import { IconMessage, IconPlus, IconTrash } from '@tabler/icons-react';
import { ChatSession } from '@smart-assistant/shared-types';

interface ChatHistoryProps {
  sessions: ChatSession[];
  activeSessionId?: string;
  onSessionSelect?: (sessionId: string) => void;
  onNewSession?: () => void;
  onDeleteSession?: (sessionId: string) => void;
}

interface SessionItemProps {
  session: ChatSession;
  isActive: boolean;
  onSelect: (sessionId: string) => void;
  onDelete: (sessionId: string) => void;
}

function SessionItem({ session, isActive, onSelect, onDelete }: SessionItemProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(session.id);
  };

  return (
    <UnstyledButton
      w="100%"
      p="sm"
      style={{
        borderRadius: '8px',
        backgroundColor: isActive ? '#e7f5ff' : 'transparent',
        border: isActive ? '1px solid #339af0' : '1px solid transparent',
        transition: 'all 0.2s ease',
      }}
      onClick={() => onSelect(session.id)}
      onMouseOver={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = '#f8f9fa';
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = 'transparent';
        }
      }}
    >
      <Group justify="space-between" align="flex-start" gap="xs">
        <Box style={{ flex: 1, minWidth: 0 }}>
          <Text
            size="sm"
            fw={500}
            lineClamp={2}
            title={session.title}
            style={{
              color: isActive ? '#339af0' : 'inherit',
            }}
          >
            {session.title}
          </Text>
          <Text size="xs" c="dimmed" mt={4}>
            {new Date(session.updatedAt).toLocaleDateString('zh-TW', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Text>
        </Box>
        
        <Box
          component="span"
          onClick={handleDelete}
          style={{
            opacity: 0.7,
            transition: 'opacity 0.2s ease',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fa5252'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.opacity = '1';
            e.currentTarget.style.backgroundColor = '#ffebee';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '0.7';
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <IconTrash size={14} />
        </Box>
      </Group>
    </UnstyledButton>
  );
}

export default function ChatHistory({ 
  sessions, 
  activeSessionId, 
  onSessionSelect = () => {},
  onNewSession = () => {},
  onDeleteSession = () => {}
}: ChatHistoryProps) {
  return (
    <Box h="100%" style={{ display: 'flex', flexDirection: 'column' }}>
      {/* 標題與新建按鈕 */}
      <Group justify="space-between" mb="md">
        <Text fw={600} size="lg">
          聊天歷史
        </Text>
        <ActionIcon
          variant="light"
          color="blue"
          size="lg"
          onClick={onNewSession}
          title="開始新對話"
        >
          <IconPlus size={18} />
        </ActionIcon>
      </Group>

      {/* 會話列表 */}
      <ScrollArea style={{ flex: 1 }} scrollbarSize={4}>
        {sessions.length === 0 ? (
          <Paper 
            p="xl" 
            style={{ 
              textAlign: 'center',
              backgroundColor: '#f8f9fa',
              border: '1px dashed #dee2e6'
            }}
          >
            <IconMessage size={32} stroke={1.5} style={{ opacity: 0.5, marginBottom: '0.5rem' }} />
            <Text size="sm" c="dimmed">
              尚無聊天記錄
            </Text>
            <Text size="xs" c="dimmed" mt={4}>
              點擊 + 開始新對話
            </Text>
          </Paper>
        ) : (
          <Stack gap="xs">
            {sessions.map((session) => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={session.id === activeSessionId}
                onSelect={onSessionSelect}
                onDelete={onDeleteSession}
              />
            ))}
          </Stack>
        )}
      </ScrollArea>
    </Box>
  );
}