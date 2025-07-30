import { useState } from 'react';
import {
  Container,
  Title,
  Card,
  TextInput,
  Button,
  Group,
  Progress,
  Text,
  Alert,
  Stack,
  Box,
  Badge,
  ActionIcon,
  Table,
  ScrollArea
} from '@mantine/core';
import { IconFolder, IconUpload, IconCheck, IconX, IconAlertCircle, IconRefresh } from '@tabler/icons-react';
import { KnowledgeBase } from '@smart-assistant/shared-types';
import { useKnowledgeBaseStore } from '../stores/knowledgeBaseStore';

export default function DocumentUploadPage() {
  const [folderPath, setFolderPath] = useState('');
  const [knowledgeBaseName, setKnowledgeBaseName] = useState('');
  
  const {
    knowledgeBases,
    currentImport,
    isLoading,
    error,
    createKnowledgeBase,
    refreshKnowledgeBases,
    clearError
  } = useKnowledgeBaseStore();

  const handlePathChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFolderPath(event.currentTarget.value);
    clearError();
  };

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setKnowledgeBaseName(event.currentTarget.value);
  };

  const handleImport = async () => {
    if (!folderPath.trim() || !knowledgeBaseName.trim()) {
      return;
    }

    await createKnowledgeBase({
      name: knowledgeBaseName.trim(),
      path: folderPath.trim()
    });

    // Clear form if successful
    if (!error) {
      setFolderPath('');
      setKnowledgeBaseName('');
    }
  };

  const getStatusColor = (status: KnowledgeBase['status']) => {
    switch (status) {
      case 'ready': return 'green';
      case 'processing': return 'blue';
      case 'error': return 'red';
      case 'pending': return 'yellow';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: KnowledgeBase['status']) => {
    switch (status) {
      case 'ready': return <IconCheck size={16} />;
      case 'processing': return <IconRefresh size={16} />;
      case 'error': return <IconX size={16} />;
      case 'pending': return <IconAlertCircle size={16} />;
      default: return null;
    }
  };

  const getStatusText = (status: KnowledgeBase['status']) => {
    switch (status) {
      case 'ready': return '已完成';
      case 'processing': return '處理中';
      case 'error': return '錯誤';
      case 'pending': return '等待中';
      default: return '未知';
    }
  };

  const isFormValid = folderPath.trim().length > 0 && knowledgeBaseName.trim().length > 0;

  return (
    <Container size="lg" py="xl">
      <Title order={1} mb="xl">文件知識庫管理</Title>
      
      <Stack gap="lg">
        {/* 上傳表單卡片 */}
        <Card withBorder shadow="sm" padding="lg">
          <Title order={2} size="h3" mb="md">
            <Group gap="xs">
              <IconFolder size={24} />
              新增知識庫
            </Group>
          </Title>
          
          <Stack gap="md">
            <TextInput
              label="知識庫名稱"
              placeholder="例如：我的專案文件"
              value={knowledgeBaseName}
              onChange={handleNameChange}
              required
              description="為您的知識庫指定一個便於識別的名稱"
            />
            
            <TextInput
              label="文件資料夾路徑"
              placeholder="例如：/home/user/documents 或 C:\\Users\\Documents"
              value={folderPath}
              onChange={handlePathChange}
              required
              leftSection={<IconFolder size={16} />}
              description="指定包含您要導入文件的本地資料夾路徑"
            />

            <Group justify="flex-end">
              <Button
                leftSection={<IconUpload size={16} />}
                onClick={handleImport}
                loading={isLoading}
                disabled={!isFormValid}
                size="md"
              >
                開始導入
              </Button>
            </Group>
          </Stack>
        </Card>

        {/* 錯誤訊息 */}
        {error && (
          <Alert
            variant="light"
            color="red"
            title="導入失敗"
            icon={<IconX size={16} />}
            withCloseButton
            onClose={clearError}
          >
            {error}
          </Alert>
        )}

        {/* 當前導入進度 */}
        {currentImport && (
          <Card withBorder shadow="sm" padding="lg">
            <Title order={3} size="h4" mb="md">
              <Group gap="xs">
                <IconRefresh size={20} />
                正在處理：{currentImport.name}
              </Group>
            </Title>
            
            <Stack gap="sm">
              <Group justify="space-between">
                <Text size="sm" c="dimmed">路徑：{currentImport.path}</Text>
                <Badge 
                  color={getStatusColor(currentImport.status)} 
                  leftSection={getStatusIcon(currentImport.status)}
                >
                  {getStatusText(currentImport.status)}
                </Badge>
              </Group>
              
              {currentImport.status === 'processing' && (
                <Progress 
                  value={50} 
                  animated 
                  color="blue"
                  size="lg"
                />
              )}
              
              {currentImport.status === 'ready' && (
                <Text size="sm" c="green">
                  成功導入 {currentImport.documentCount} 個文件
                </Text>
              )}
              
              {currentImport.status === 'error' && currentImport.errorDetails && (
                <Alert variant="light" color="red" icon={<IconX size={16} />}>
                  {currentImport.errorDetails}
                </Alert>
              )}
            </Stack>
          </Card>
        )}

        {/* 知識庫列表 */}
        <Card withBorder shadow="sm" padding="lg">
          <Group justify="space-between" mb="md">
            <Title order={3} size="h4">已建立的知識庫</Title>
            <ActionIcon
              variant="light"
              onClick={refreshKnowledgeBases}
              loading={isLoading}
            >
              <IconRefresh size={16} />
            </ActionIcon>
          </Group>

          {knowledgeBases.length === 0 ? (
            <Box ta="center" py="xl">
              <Text c="dimmed">尚未建立任何知識庫</Text>
              <Text size="sm" c="dimmed" mt="xs">
                使用上方表單來建立您的第一個知識庫
              </Text>
            </Box>
          ) : (
            <ScrollArea>
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>名稱</Table.Th>
                    <Table.Th>路徑</Table.Th>
                    <Table.Th>狀態</Table.Th>
                    <Table.Th>文件數量</Table.Th>
                    <Table.Th>建立時間</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {knowledgeBases.map((kb) => (
                    <Table.Tr key={kb.id}>
                      <Table.Td>
                        <Text fw={500}>{kb.name}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm" c="dimmed" style={{ 
                          maxWidth: '200px', 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {kb.path}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Badge 
                          color={getStatusColor(kb.status)} 
                          leftSection={getStatusIcon(kb.status)}
                          size="sm"
                        >
                          {getStatusText(kb.status)}
                        </Badge>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm">
                          {kb.status === 'ready' ? kb.documentCount : '-'}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm" c="dimmed">
                          {kb.importedAt ? new Date(kb.importedAt).toLocaleDateString('zh-TW') : '-'}
                        </Text>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </ScrollArea>
          )}
        </Card>
      </Stack>
    </Container>
  );
}