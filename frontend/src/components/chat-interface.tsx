'use client'
import { useState, useEffect } from 'react'
import { Sidebar } from './sidebar'
import { ChatArea } from './chat-area'
import { InputArea } from './input-area'
import { PanelLeftOpen, PanelLeftClose } from 'lucide-react'
import { Button } from "@/components/ui/button"

import { api } from '../api/index'


export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant'
}

export interface Conversation {
  id: number
  title: string
  messages: Message[]
}

export default function ChatGPTLikeInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isTyping, setIsTyping] = useState(false)

  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations')
    if (savedConversations) {
      const parsedConversations = JSON.parse(savedConversations)
      setConversations(parsedConversations)
      if (parsedConversations.length > 0) {
        setCurrentConversation(parsedConversations[0])
      }
    } else {
      const initialConversation: Conversation = {
        id: 1,
        title: 'Welcome Chat',
        messages: [{ id: 1, content: "Hello! How can I assist you today?", role: 'assistant' }]
      }
      setConversations([initialConversation])
      setCurrentConversation(initialConversation)
    }
  }, [])

  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations))
    }
  }, [conversations])

  const addMessage = async (content: string) => {
    if (!currentConversation) return

    const newMessage: Message = {
      id: currentConversation.messages.length + 1,
      content,
      role: 'user'
    }

    const updatedConversation = {
      ...currentConversation,
      messages: [...currentConversation.messages, newMessage]
    }

    setCurrentConversation(updatedConversation)
    setConversations(conversations.map(conv => 
      conv.id === currentConversation.id ? updatedConversation : conv
    ))

    setIsTyping(true)

    try {
      const response = await api.post('/api/chat-naiverag', { query: content })

      if (!response.data) {
        throw new Error('Failed to fetch response from API')
      }
      const data = response.data


      const assistantMessage: Message = {
        id: updatedConversation.messages.length + 1,
        content: data.response,
        role: 'assistant'
      }

      const finalConversation = {
        ...updatedConversation,
        messages: [...updatedConversation.messages, assistantMessage]
      }

      setCurrentConversation(finalConversation)
      setConversations(conversations.map(conv => 
        conv.id === currentConversation.id ? finalConversation : conv
      ))
    } catch (error) {
      console.error('Error fetching response:', error)
      const errorMessage: Message = {
        id: updatedConversation.messages.length + 1,
        content: "I'm sorry, I encountered an error while processing your request.",
        role: 'assistant'
      }
      const finalConversation = {
        ...updatedConversation,
        messages: [...updatedConversation.messages, errorMessage]
      }
      setCurrentConversation(finalConversation)
      setConversations(conversations.map(conv => 
        conv.id === currentConversation.id ? finalConversation : conv
      ))
    } finally {
      setIsTyping(false)
    }
  }

  const startNewConversation = () => {
    const newConversation: Conversation = {
      id: conversations.length + 1,
      title: `New Chat ${conversations.length + 1}`,
      messages: []
    }
    setConversations([...conversations, newConversation])
    setCurrentConversation(newConversation)
  }

  const renameConversation = (id: number, newTitle: string) => {
    const updatedConversations = conversations.map(conv =>
      conv.id === id ? { ...conv, title: newTitle } : conv
    )
    setConversations(updatedConversations)
    if (currentConversation && currentConversation.id === id) {
      setCurrentConversation({ ...currentConversation, title: newTitle })
    }
  }

  const deleteConversation = (id: number) => {
    const updatedConversations = conversations.filter(conv => conv.id !== id)
    setConversations(updatedConversations)
    if (currentConversation && currentConversation.id === id) {
      setCurrentConversation(updatedConversations[0] || null)
    }
  }

  return (
    <div className="flex h-screen bg-gray-100 relative">
      <Sidebar 
        conversations={conversations}
        currentConversation={currentConversation || conversations[0]}
        setCurrentConversation={setCurrentConversation}
        startNewConversation={startNewConversation}
        renameConversation={renameConversation}
        deleteConversation={deleteConversation}
        isOpen={sidebarOpen}
      />
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 z-30 transition-all duration-300 ease-in-out ${
          sidebarOpen ? 'left-[260px]' : 'left-4'
        }`}
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        <span className="sr-only">{sidebarOpen ? 'Close sidebar' : 'Open sidebar'}</span>
      </Button>
      <div className={`flex flex-col flex-grow transition-all duration-300 ease-in-out ${
        sidebarOpen ? 'ml-64' : 'ml-0'
      }`}>
        <ChatArea messages={currentConversation?.messages || []} isTyping={isTyping} />
        <InputArea onSendMessage={addMessage} />
      </div>
    </div>
  )
}