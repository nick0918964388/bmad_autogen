import { useChatStore } from './chatStore';

// Mock setTimeout for sendMessage simulation
jest.useFakeTimers();

describe('chatStore', () => {
  beforeEach(() => {
    // 重置 store 狀態
    useChatStore.getState().clearAllSessions();  
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  test('initial state should be correct', () => {
    const state = useChatStore.getState();
    
    expect(state.sessions).toEqual([]);
    expect(state.activeSessionId).toBeNull();
    expect(state.messages).toEqual({});
    expect(state.isLoading).toBe(false);
  });

  test('createSession should create a new session', () => {
    const store = useChatStore.getState();
    
    const sessionId = store.createSession('測試會話');
    const state = useChatStore.getState();
    
    expect(state.sessions).toHaveLength(1);
    expect(state.sessions[0].title).toBe('測試會話');
    expect(state.sessions[0].id).toBe(sessionId);
    expect(state.activeSessionId).toBe(sessionId);
    expect(state.messages[sessionId]).toEqual([]);
  });

  test('createSession without title should generate default title', () => {
    const store = useChatStore.getState();
    
    store.createSession();
    const state = useChatStore.getState();
    
    expect(state.sessions).toHaveLength(1);
    expect(state.sessions[0].title).toMatch(/新對話/);
  });

  test('selectSession should set active session', () => {
    const store = useChatStore.getState();
    
    const sessionId1 = store.createSession('會話1');
    const sessionId2 = store.createSession('會話2');
    
    // 創建第二個會話後，它應該是活動會話
    expect(useChatStore.getState().activeSessionId).toBe(sessionId2);
    
    // 切換到第一個會話
    store.selectSession(sessionId1);
    expect(useChatStore.getState().activeSessionId).toBe(sessionId1);
  });

  test('deleteSession should remove session and its messages', () => {
    const store = useChatStore.getState();
    
    const sessionId1 = store.createSession('會話1');
    const sessionId2 = store.createSession('會話2');
    
    // 添加一些訊息
    store.addMessage(sessionId1, {
      sessionId: sessionId1,
      sender: 'user',
      content: '測試訊息'
    });
    
    let state = useChatStore.getState();
    expect(state.sessions).toHaveLength(2);
    expect(state.messages[sessionId1]).toHaveLength(1);
    
    // 刪除會話1
    store.deleteSession(sessionId1);
    
    state = useChatStore.getState();
    expect(state.sessions).toHaveLength(1);
    expect(state.sessions[0].id).toBe(sessionId2);
    expect(state.messages[sessionId1]).toBeUndefined();
  });

  test('deleteSession should update activeSessionId when deleting active session', () => {
    const store = useChatStore.getState();
    
    const sessionId1 = store.createSession('會話1');
    const sessionId2 = store.createSession('會話2');
    
    // 會話2是活動會話
    expect(useChatStore.getState().activeSessionId).toBe(sessionId2);
    
    // 刪除活動會話
    store.deleteSession(sessionId2);
    
    // 應該切換到剩餘的會話
    expect(useChatStore.getState().activeSessionId).toBe(sessionId1);
  });

  test('addMessage should add message to correct session', () => {
    const store = useChatStore.getState();
    
    const sessionId = store.createSession('測試會話');
    
    store.addMessage(sessionId, {
      sessionId,
      sender: 'user',
      content: '測試訊息'
    });
    
    const state = useChatStore.getState();
    const messages = state.messages[sessionId];
    expect(messages).toHaveLength(1);
    expect(messages[0].content).toBe('測試訊息');
    expect(messages[0].sender).toBe('user');
    expect(messages[0].id).toBeDefined();
    expect(messages[0].timestamp).toBeInstanceOf(Date);
  });

  test('sendMessage should create session if none exists', async () => {
    const store = useChatStore.getState();
    
    const sendPromise = store.sendMessage('首條訊息');
    
    // 檢查是否創建了會話
    let state = useChatStore.getState();
    expect(state.sessions).toHaveLength(1);
    expect(state.activeSessionId).not.toBeNull();
    
    // 檢查是否設置了載入狀態
    expect(state.isLoading).toBe(true);
    
    // 快進時間完成模擬 API 呼叫
    jest.advanceTimersByTime(1000);
    
    await sendPromise;
    
    // 檢查載入狀態已重置
    state = useChatStore.getState();
    expect(state.isLoading).toBe(false);
    
    // 檢查訊息已添加
    const messages = state.getActiveMessages();
    expect(messages).toHaveLength(2); // 使用者訊息 + 助理回應
    expect(messages[0].sender).toBe('user');
    expect(messages[0].content).toBe('首條訊息');
    expect(messages[1].sender).toBe('assistant');
  });

  test('setLoading should update loading state', () => {
    const store = useChatStore.getState();
    
    store.setLoading(true);
    expect(useChatStore.getState().isLoading).toBe(true);
    
    store.setLoading(false);
    expect(useChatStore.getState().isLoading).toBe(false);
  });

  test('getActiveSession should return active session', () => {
    const store = useChatStore.getState();
    
    const sessionId = store.createSession('活動會話');
    
    const activeSession = store.getActiveSession();
    expect(activeSession).not.toBeNull();
    expect(activeSession?.id).toBe(sessionId);
    expect(activeSession?.title).toBe('活動會話');
  });

  test('getActiveSession should return null when no active session', () => {
    const store = useChatStore.getState();
    
    const activeSession = store.getActiveSession();
    expect(activeSession).toBeNull();
  });

  test('getActiveMessages should return messages for active session', () => {
    const store = useChatStore.getState();
    
    const sessionId = store.createSession('測試會話');
    
    store.addMessage(sessionId, {
      sessionId,
      sender: 'user',
      content: '測試訊息'
    });
    
    const activeMessages = store.getActiveMessages();
    expect(activeMessages).toHaveLength(1);
    expect(activeMessages[0].content).toBe('測試訊息');
  });

  test('getActiveMessages should return empty array when no active session', () => {
    const store = useChatStore.getState();
    
    const activeMessages = store.getActiveMessages();
    expect(activeMessages).toEqual([]);
  });

  test('clearAllSessions should reset all state', () => {
    const store = useChatStore.getState();
    
    store.createSession('會話1');
    store.createSession('會話2');
    store.setLoading(true);
    
    let state = useChatStore.getState();
    expect(state.sessions).toHaveLength(2);
    expect(state.isLoading).toBe(true);
    
    store.clearAllSessions();
    
    state = useChatStore.getState();
    expect(state.sessions).toEqual([]);
    expect(state.activeSessionId).toBeNull();
    expect(state.messages).toEqual({});
    expect(state.isLoading).toBe(false);
  });
});