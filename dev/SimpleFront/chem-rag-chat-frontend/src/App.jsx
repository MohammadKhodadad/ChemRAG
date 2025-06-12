// src/App.jsx
import React, { useState } from 'react';
import {
  Container,
  Stack,
  Paper,
  Text,
  Anchor,
  Box,
  Group,
  ThemeIcon,
} from '@mantine/core';
import axios from 'axios';
import { InputWithButton } from './components/InputWithButton';
// 1. Import the Navbar
import { Navbar } from './components/navbar';

export default function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const renderContent = (content) => {
    const parts = content.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) =>
      i % 2 === 1 ? (
        <Text component="span" weight={700} key={i}>
          {part}
        </Text>
      ) : (
        <Text component="span" key={i}>
          {part}
        </Text>
      )
    );
  };

  const sendMessage = async () => {
    if (!query.trim()) return;
    const userMsg = { role: 'user', content: query };
    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setQuery('');
    setLoading(true);

    try {
      const resp = await axios.post('/ask', {
        query: userMsg.content,
        history: newHistory,
      });
      const { answer, sources } = resp.data;
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: answer, sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error fetching response.', sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* 2. Render Navbar above everything */}
      <Navbar />

      <Container size="sm" py="xl">
        <Stack spacing="md">
          <Paper
            shadow="md"
            p="lg"
            style={{
              maxHeight: '100vh',
              overflowY: 'auto',
              backgroundColor: '#f5f7fa',
            }}
          >
            {messages.map((m, i) => (
              <Group key={i} align="start" mb="sm">
                <ThemeIcon
                  size="sm"
                  radius="xl"
                  color={m.role === 'user' ? 'blue' : 'gray'}
                >
                  {m.role === 'user' ? '👤' : '🤖'}
                </ThemeIcon>
                <Box
                  sx={(theme) => ({
                    backgroundColor:
                      m.role === 'user'
                        ? theme.fn.lighten(theme.colors.blue[5], 0.4)
                        : theme.colors.gray[2],
                    padding: theme.spacing.sm,
                    borderRadius: theme.radius.md,
                    width: '100%',
                  })}
                >
                  <Text
                    weight={m.role === 'user' ? 500 : 700}
                    color={m.role === 'user' ? 'blue.7' : 'dark'}
                    mb="xs"
                  >
                    {m.role === 'user' ? 'You' : 'Bot'}
                  </Text>
                  <Box>{renderContent(m.content)}</Box>
                  {m.sources && m.sources.length > 0 && (
                    <Stack spacing={4} mt="sm">
                      <Text size="xs" color="dimmed">
                        Sources:
                      </Text>
                      {m.sources.map((src, idx) => (
                        <Anchor
                          key={idx}
                          href={src}
                          target="_blank"
                          size="xs"
                          color="blue"
                        >
                          {src}
                        </Anchor>
                      ))}
                    </Stack>
                  )}
                </Box>
              </Group>
            ))}
          </Paper>

          <InputWithButton
            value={query}
            onChange={(e) => setQuery(e.currentTarget.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
            disabled={loading}
            onClick={sendMessage}
          />
        </Stack>
      </Container>
    </>
  );
}
