'use client'
import { useState, useEffect } from 'react'
import { Sidebar } from './sidebar'
import { RightSidebar } from './right-sidebar'
import { ChatArea } from './chat-area'
import { InputArea } from './input-area'
import { PanelLeftOpen, PanelLeftClose,PanelRightOpen, PanelRightClose } from 'lucide-react'
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

// A sample Document array to be passed to the RightSidebar component
const sampleDocuments: Document[] = [
  {
    id: 1,
    snippet: "This shift isn't just about minimizing environmental impact.",
    content: "This shift isn't just about minimizing environmental impact. It's about reimagining our relationship with resources, fostering innovation in sustainable technologies, and creating a more resilient global economy. The transition to a circular economy represents a fundamental change in how we produce, consume, and dispose of goods."
  },
  {
    id: 2,
    snippet: "The defense has sought to raise questions about the digital evidence in the",
    content: "The defense has sought to raise questions about the digital evidence in the case, arguing that the prosecution's reliance on cell phone location data and social media activity is not as conclusive as they claim. They contend that such digital footprints can be misleading or manipulated, and should not be the sole basis for determining the defendant's whereabouts or actions on the day in question."
  },
  {
    id: 3,
    snippet: "Location history data for a cell phone tied to Jose Antonio Ibarra",
    content: "Location history data for a cell phone tied to Jose Antonio Ibarra, who is accused of killing nursing student Laken Riley, placed his phone \"very close\" to Laken Riley at the time of her killing, FBI Special Agent James \"Jay\" Berni testified in court Monday. The data showed Ibarra's phone was in the area of the crime scene on the morning of February 22, the day Riley was killed, according to Berni's testimony."
  }
]

export default function ChatGPTLikeInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [isTyping, setIsTyping] = useState(false)

  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)
  const [showDocuments, setShowDocuments] = useState(true); // Added state for document visibility


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
    setShowDocuments(false)  // Reset showDocuments when starting a new conversation

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
        setShowDocuments={setShowDocuments} // Pass setShowDocuments to Sidebar
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
      <RightSidebar documents={sampleDocuments} isOpen={rightSidebarOpen} showDocuments={showDocuments}/> {/*Added showDocuments prop*/}
    </div>
  )

}