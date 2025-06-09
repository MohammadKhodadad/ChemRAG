// src/components/InputWithButton.jsx
import React from 'react';
import { ActionIcon, TextInput, useMantineTheme } from '@mantine/core';

export function InputWithButton(props) {
  const theme = useMantineTheme();

  return (
    <TextInput
      radius="xl"
      size="md"
      placeholder="Type your question"
      rightSectionWidth={42}
      rightSection={
        <ActionIcon
          size={32}
          radius="xl"
          color="blue"
          variant="filled"
          onClick={props.onClick}
        >
          ➤
        </ActionIcon>
      }
      {...props}
    />
  );
}
