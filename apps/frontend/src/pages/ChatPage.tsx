import { AppShell, Box } from '@mantine/core';
import { useChatStore } from '../stores/chatStore';
import ChatWindow from '../components/chat/ChatWindow';
import ChatHistory from '../components/chat/ChatHistory';
import MessageInput from '../components/chat/MessageInput';

export default function ChatPage() {
  const {
    sessions,
    activeSessionId,
    isLoading,
    getActiveMessages,
    createSession,
    selectSession,
    deleteSession,
    sendMessage
  } = useChatStore();

  const activeMessages = getActiveMessages();

  const handleNewSession = () => {
    createSession();
  };

  const handleSessionSelect = (sessionId: string) => {
    selectSession(sessionId);
  };

  const handleSessionDelete = (sessionId: string) => {
    deleteSession(sessionId);
  };

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  return (
    <AppShell
      header={{ height: 0 }}
      navbar={{ 
        width: 300, 
        breakpoint: 'sm', 
        collapsed: { mobile: true, desktop: false } 
      }}
      padding={0}
    >
      <AppShell.Navbar p="md">
        <ChatHistory
          sessions={sessions}
          activeSessionId={activeSessionId || undefined}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
          onDeleteSession={handleSessionDelete}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        <Box style={{ 
          height: '100vh', 
          display: 'flex', 
          flexDirection: 'column' 
        }}>
          {/* 主對話區 */}
          <Box style={{ flex: 1, overflow: 'hidden' }}>
            <ChatWindow 
              messages={activeMessages}
              isLoading={isLoading}
            />
          </Box>

          {/* 底部輸入區 */}
          <MessageInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            placeholder="請輸入您的訊息..."
            disabled={false}
          />
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}