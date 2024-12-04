'use client'

import { useState } from 'react'
import { Sidebar } from './sidebar'
import { ChatArea } from './chat-area'
import { InputArea } from './input-area'
import { PanelLeftOpen, PanelLeftClose } from 'lucide-react'
import { Button } from "@/components/ui/button"

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

export default function ChatInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: 1, title: 'Welcome Chat', messages: [{ id: 1, content: "Hello! How can I assist you today?", role: 'assistant' }] }
  ])
  const [currentConversation, setCurrentConversation] = useState<Conversation>(conversations[0])
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const addMessage = (content: string) => {
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

    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: updatedConversation.messages.length + 1,
        content: "Thank you for your message. I'm processing your request.",
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
    }, 1000)
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

  return (
    <div className="flex h-screen bg-gray-100 relative">
      <Sidebar 
        conversations={conversations}
        currentConversation={currentConversation}
        setCurrentConversation={setCurrentConversation}
        startNewConversation={startNewConversation}
        isOpen={sidebarOpen}
      />
      <Button
        variant="outline"
        size="icon"
        className={`opacity-10 hover:opacity-100 fixed top-4 z-30 transition-all duration-300 ease-in-out ${
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
        <ChatArea messages={currentConversation.messages} />
        <InputArea onSendMessage={addMessage} />
      </div>
    </div>
  )
}

