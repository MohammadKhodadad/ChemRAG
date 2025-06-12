// src/components/navbar.jsx
import React from 'react';
import {
  Box,
  Group,
  Anchor,
  Burger,
  Button,
  Drawer,
  ScrollArea,
  Divider,
  Center,
  Text,
  useMantineTheme,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';

export function Navbar() {
  const theme = useMantineTheme();
  const [drawerOpened, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);

  const linkStyles = {
    display: 'block',
    padding: '0.5rem 1rem',
    fontWeight: 500,
    color: theme.colors.dark[7],
    textDecoration: 'none',
    '&:hover': {
      color: theme.colors.blue[6],
    },
  };

  return (
    <Box>
      {/* desktop / tablet */}
      <Group
        position="apart"
        align="center"
        px="md"
        py="sm"
        style={{ borderBottom: `1px solid ${theme.colors.gray[2]}` }}
      >
        {/* Text logo */}
        <Text weight={700} size="lg">
          ChemRAG
        </Text>

        {/* nav links ≥ sm */}
        <Group spacing="md" visibleFrom="sm">
          <Anchor href="/" sx={linkStyles}>
            Home
          </Anchor>
        </Group>

        {/* auth buttons ≥ sm */}
        <Group spacing="sm" visibleFrom="sm">
          <Button variant="default" size="xs">
            Sign In
          </Button>
          <Button size="xs">Sign Up</Button>
        </Group>

        {/* burger for < sm */}
        <Burger opened={drawerOpened} onClick={toggleDrawer} hiddenFrom="sm" />
      </Group>

      {/* mobile drawer */}
      <Drawer
        opened={drawerOpened}
        onClose={closeDrawer}
        size="100%"
        padding="md"
        title="Menu"
        hiddenFrom="sm"
        zIndex={1000000}
      >
        <ScrollArea style={{ height: 'calc(100vh - 60px)' }} mx="-md">
          <Divider my="sm" />

          <Anchor href="/" sx={linkStyles}>
            Home
          </Anchor>

          <Divider my="sm" />

          <Center>
            <Group spacing="sm" grow>
              <Button variant="default" fullWidth size="md">
                Sign In
              </Button>
              <Button fullWidth size="md">
                Sign Up
              </Button>
            </Group>
          </Center>
        </ScrollArea>
      </Drawer>
    </Box>
  );
}
