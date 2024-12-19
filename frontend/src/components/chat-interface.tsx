'use client'
import { useState, useEffect } from 'react'
import { Sidebar } from './sidebar'
import { RightSidebar } from './right-sidebar'
import { ChatArea } from './chat-area'
import { InputArea } from './input-area'
import { PanelLeftOpen, PanelLeftClose, PanelRightOpen, PanelRightClose } from 'lucide-react'
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

interface Document {
  id: number
  snippet: string
  content: string
}

export default function ChatInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [isTyping, setIsTyping] = useState(false)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)

  // State to hold documents returned from the API
  const [documents, setDocuments] = useState<Document[]>([])
  // Control whether documents are shown in the right sidebar
  const [showDocuments, setShowDocuments] = useState(true);



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

    setShowDocuments(true) // Show documents when a question is asked
    setDocuments([]) // Clear previous documents before fetching new ones

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
      // Call the updated API endpoint
      const response = await api.post('/api/process-query', { query: content })

      if (!response.data) {
        throw new Error('Failed to fetch response from API')
      }

      const data = response.data

      // The API now returns `final_response` instead of `response`
      const assistantMessage: Message = {
        id: updatedConversation.messages.length + 1,
        content: data.final_response,
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

      // Process documents returned by the API
      if (data.texts && data.texts.documents) {
        const newDocuments: Document[] = data.texts.documents.map((doc: string, index: number) => ({
          id: data.texts.fragment_ids[index],
          snippet: doc.substring(0, 100) + (doc.length > 100 ? '...' : ''),
        }))
        setDocuments(newDocuments)
      }

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
    setShowDocuments(false)  // Reset showDocuments when starting a new conversation
    setDocuments([]) // Clear documents
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
        currentConversation={currentConversation}
        setCurrentConversation={setCurrentConversation}
        startNewConversation={startNewConversation}
        renameConversation={renameConversation}
        deleteConversation={deleteConversation}
        isOpen={leftSidebarOpen}
        setShowDocuments={setShowDocuments}
      />
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 z-30 transition-all duration-300 ease-in-out ${
          leftSidebarOpen ? 'left-[260px]' : 'left-4'
        }`}
        onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
      >
        {leftSidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        <span className="sr-only">{leftSidebarOpen ? 'Close left sidebar' : 'Open left sidebar'}</span>
      </Button>
      <div className={`flex flex-col flex-grow transition-all duration-300 ease-in-out ${
        leftSidebarOpen ? 'ml-64' : 'ml-0'
      } ${
        rightSidebarOpen ? 'mr-64' : 'mr-0'
      }`}>
        <ChatArea messages={currentConversation?.messages || []} isTyping={isTyping} />
        <InputArea onSendMessage={addMessage} />
      </div>
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 right-4 z-30 transition-all duration-300 ease-in-out ${
          rightSidebarOpen ? 'right-[260px]' : 'right-4'
        }`}
        onClick={() => setRightSidebarOpen(!rightSidebarOpen)}
      >
        {rightSidebarOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRightOpen className="h-4 w-4" />}
        <span className="sr-only">{rightSidebarOpen ? 'Close right sidebar' : 'Open right sidebar'}</span>
      </Button>

      {/* Pass the dynamically fetched documents to the RightSidebar */}
      <RightSidebar documents={documents} isOpen={rightSidebarOpen} showDocuments={showDocuments}/>
    </div>
  )
}
