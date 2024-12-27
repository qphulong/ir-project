'use client'
import { useState, useEffect, ChangeEvent } from 'react'
import { Sidebar } from './sidebar'
import { RightSidebar } from './right-sidebar'
import { ChatArea } from './chat-area'
import { InputArea } from './input-area'
import { PanelLeftOpen, PanelLeftClose, PanelRightOpen, PanelRightClose, CircleAlert, FileIcon } from 'lucide-react'
import { Button } from "@/components/ui/button"
import useWebSocket, { ReadyState } from "react-use-websocket"
import { Input } from './ui/input'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip'
import { api } from '@/api'
import { useToast } from '@/hooks/use-toast'
import { Spinner } from './ui/spinner'

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
  id: string
  snippet: string
  content: string
}

interface Image {
  id: string
  url: string
}

enum QueryState {
  NONE,
  SEARCHING_LOCAL,
  SEARCHING_INTERNET,
  PENDING,
  SUCCESS,
  ERROR
}

export const ACCEPTED_DOCUMENT_MIME_TYPES = new Set<string>(['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']);

export const FILE_INPUT_ACCEPT_VALUE = Array.from(ACCEPTED_DOCUMENT_MIME_TYPES).join(',');

export default function ChatInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [isTyping, setIsTyping] = useState(false)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)
  const [isInputAreaDisabled, setIsInputAreaDisabled] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [canUpload, setCanUpload] = useState(true)
  const { toast } = useToast()
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket("ws://localhost:4000/api/process-query", {
    share: true
  });

  // State to hold documents returned from the API
  const [documents, setDocuments] = useState<Document[] | null>(null)
  const [images, setImages] = useState<Image[] | null>(null)
  // Control whether documents are shown in the right sidebar
  const [showDocuments, setShowDocuments] = useState(false);
  // State to hold the preprocessed query
  const [preprocessedQuery, setPreprocessedQuery] = useState<string | null>(null);

  function handleResize() {
    if (window.innerWidth < 768) {
      setIsMobile(true)
      setLeftSidebarOpen(false)
      setRightSidebarOpen(false)
    } else {
      setIsMobile(false)
    }
  }

  useEffect(() => {
    // Add event listener to handle window resize
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("WebSocket connection established");
    } else if (readyState === ReadyState.CLOSED) {
      console.log("WebSocket connection closed");
      setIsInputAreaDisabled(true)
    }
  }, [readyState]);
  
  useEffect(() => {
    if (lastJsonMessage && currentConversation) {
      const message = lastJsonMessage as any;
      switch (message.state) {
        case QueryState.SEARCHING_LOCAL:
          setIsTyping(true);
          break;
        case QueryState.SEARCHING_INTERNET:
          setIsTyping(false);
          const assistantInternetRequiredMessage: Message = {
            id: currentConversation.messages.length + 1,
            content: "Searching the internet for relevant information... This may take a while.",
            role: 'assistant'
          }
          const updatedConversationInternetRequired = {
            ...currentConversation,
            messages: [...currentConversation.messages, assistantInternetRequiredMessage]
          }
          setCurrentConversation(updatedConversationInternetRequired)
          setConversations(conversations.map(conv =>
            conv.id === currentConversation.id ? updatedConversationInternetRequired : conv
          ))
          setIsTyping(true);
          break;
        case QueryState.SUCCESS:
          const assistantMessage: Message = {
            id: currentConversation.messages.length + 1,
            content: message.result.final_response,
            role: 'assistant'
          }
    
          const updatedConversation = {
            ...currentConversation,
            messages: [...currentConversation.messages, assistantMessage]
          }
    
          setCurrentConversation(updatedConversation)
          setConversations(conversations.map(conv =>
            conv.id === currentConversation.id ? updatedConversation : conv
          ))
    
          // Process documents returned by the API
          if (message.result.texts && message.result.texts.documents) {
            const newDocuments: Document[] = message.result.texts.documents.map((doc: string, index: number) => ({
              id: message.result.texts.fragment_ids[index],
              snippet: doc
            }))
            const newImages: Image[] = message.result.images.urls.map((url: string, index: number) => ({
              id: message.result.images.fragment_ids[index],
              url: url
            }))
            setDocuments(newDocuments)
            setImages(newImages)
          }
          setIsTyping(false)
          break;
        case QueryState.ERROR:
          const errorMessage: Message = {
            id: currentConversation.messages.length + 1,
            content: "I'm sorry, I encountered an error while processing your request.",
            role: 'assistant'
          }
          const finalConversation = {
            ...currentConversation,
            messages: [...currentConversation.messages, errorMessage]
          }
          setCurrentConversation(finalConversation)
          setConversations(conversations.map(conv =>
            conv.id === currentConversation.id ? finalConversation : conv
          ))
          setIsTyping(false)
          break;
      }
    }
  }, [lastJsonMessage]);

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
        messages: [{ id: 1, content: "Hello! Please start by asking a question.", role: 'assistant' }]
      }
      setConversations([initialConversation])
      setCurrentConversation(initialConversation)
    }
  }, [])

  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations))
      setIsInputAreaDisabled(false)
    } else {
      localStorage.removeItem('conversations')
      setIsInputAreaDisabled(true)
    }
  }, [conversations])

  const addMessage = async (content: string) => {
    if (!currentConversation) return

    setShowDocuments(true) // Show documents when a question is asked
    setDocuments(null) // Clear previous documents before fetching new ones
    setImages(null)

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

    sendJsonMessage({ query: content })
    setIsInputAreaDisabled(true)
  }

  const startNewConversation = () => {
    const newConversation: Conversation = {
      id: conversations.length + 1,
      title: `New Chat ${conversations.length + 1}`,
      messages: [{ id: 1, content: "Hello! Please start by asking a question.", role: 'assistant' }]
    }
    setConversations([...conversations, newConversation])
    setCurrentConversation(newConversation)
    setShowDocuments(false)  // Reset showDocuments when starting a new conversation
    setDocuments(null) // Clear documents when starting a new conversation
    setImages(null) // Clear images when starting a new conversation
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

  async function onFileInputChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      if (!ACCEPTED_DOCUMENT_MIME_TYPES.has(file?.type)) {
          toast({
            variant: "destructive",
            title: "Invalid file type",
            description: "Please upload a valid document type (PDF, DOCX)."
          })
          return;
      }
      setCanUpload(false);
      try {
        const formData = new FormData();
        formData.append('file', file);
        await api.postForm('/api/upload-document', formData);
      }
      catch (error) {
        toast({
          variant: "destructive",
          title: "Upload failed",
          description: "An error occurred while uploading the document."
        })
      }
      finally {
        e.target.value = '';
        setCanUpload(true);
      }
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
        onPreprocessQuery={(query, action) => {
          if (action === 'append') {
            setPreprocessedQuery(preprocessedQuery ? `${preprocessedQuery} ${query}` : query)
          } else {
            setPreprocessedQuery(query)
          }
        }}
      />
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 z-30 transition-all duration-300 ease-in-out ${
          leftSidebarOpen ? 'left-4 md:left-[260px]' : 'left-4'
        }`}
        onClick={() => {
          if (!(isMobile && rightSidebarOpen)) {
            setLeftSidebarOpen(!leftSidebarOpen)
          }
        }}
        >
        {leftSidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        <span className="sr-only">{leftSidebarOpen ? 'Close left sidebar' : 'Open left sidebar'}</span>
      </Button>
      <div className={`flex flex-col flex-grow transition-all duration-300 ease-in-out ${
        leftSidebarOpen ? 'md:ml-64' : 'ml-0'
      } ${
        rightSidebarOpen ? 'md:mr-64' : 'mr-0'
      }`}>
        {readyState === ReadyState.CLOSED ?
        <div className="h-full flex flex-col gap-2 items-center justify-center text-center p-4 text-gray-500">
          <CircleAlert size={48}/>
          <p className="text-xl ">Unable to establish connection with the chat API. Try to refresh this page.</p>
        </div> :
        <ChatArea messages={currentConversation?.messages || []} isTyping={isTyping} />}
        <div className='flex bg-white items-center'>
          <div className='pl-4 py-4 h-full'>
          <TooltipProvider delayDuration={350} skipDelayDuration={150}>
            <Tooltip>
              <TooltipTrigger asChild>
                <label
                  htmlFor="file-upload"
                  className={"cursor-pointer h-full flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 bg-primary text-primary-foreground shadow hover:bg-primary/90 px-4 py-2" + (canUpload ? "" : " pointer-events-none")}
                >
                  {canUpload ?
                  <FileIcon /> :
                  <Spinner /> }
                </label>
              </TooltipTrigger>
              <Input id="file-upload" type="file" className="hidden" accept={FILE_INPUT_ACCEPT_VALUE} onChange={onFileInputChange}/>
              <TooltipContent side="bottom">
                Upload a new file
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          </div>
          <InputArea onSendMessage={addMessage} preprocessedQuery={preprocessedQuery} disabled={isTyping || isInputAreaDisabled}/>
        </div>
      </div>
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 right-4 z-30 transition-all duration-300 ease-in-out ${
          rightSidebarOpen ? 'right-4 md:right-[260px]' : 'right-4'
        }`}
        onClick={() => {
          if (!(isMobile && leftSidebarOpen)) {
            setRightSidebarOpen(!rightSidebarOpen)
          }
        }}
      >
        {rightSidebarOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRightOpen className="h-4 w-4" />}
        <span className="sr-only">{rightSidebarOpen ? 'Close right sidebar' : 'Open right sidebar'}</span>
      </Button>

      {/* Pass the dynamically fetched documents to the RightSidebar */}
      <RightSidebar images={images} documents={documents} isOpen={rightSidebarOpen} showDocuments={showDocuments}/>
    </div>
  )
}
