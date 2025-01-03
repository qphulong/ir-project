import { Conversation } from './chat-interface'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PlusCircle, Pencil, Search, Replace, PlusCircleIcon } from 'lucide-react'
// import { Conversation } from './chatgpt-like-interface'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"

import { api } from '@/api'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Progress } from '@/components/ui/progress'
interface SidebarProps {
  conversations: Conversation[]
  currentConversation: Conversation | null
  setCurrentConversation: (conversation: Conversation) => void
  startNewConversation: () => void
  renameConversation: (id: number, newTitle: string) => void
  deleteConversation: (id: number) => void
  setShowDocuments: (showDocuments: boolean) => void
  isOpen: boolean
  onPreprocessQuery: (query: string, action: "append" | "replace") => void
}

export function Sidebar({ 
  conversations, 
  currentConversation, 
  setCurrentConversation, 
  startNewConversation,
  renameConversation,
  deleteConversation,
  // setShowDocuments,
  isOpen,
  onPreprocessQuery
}: SidebarProps) {
  const [newTitle, setNewTitle] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<string[]>([])
  const searchResultsRef = useRef<HTMLUListElement>(null)
  const [searchState, setSearchState] = useState<"idle" | "loading" | "error">("idle")

  useEffect(() => {
    if (searchResultsRef.current) {
      searchResultsRef.current.scrollTop = 0
    }
  }, [searchResults])

  if (!isOpen) return null

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim() === '') {
      setSearchResults([])
      return
    }

    let results =[]
    try {
      setSearchState("loading")
      // Call the updated API endpoint
      const response = await api.post('/api/preprocess-query', { query: searchQuery })
      if (!response.data) {
        throw new Error('Failed to fetch response from API')
      }
      const data = response.data
      results = data.response
      setSearchState("idle")
    }
    catch (error) {
      setSearchState("error")
      results.push('Failed to fetch response from API')
    }

    
    // // Simulated search results
    // const results = [
    //   `What is the best way to learn ${searchQuery}?`,
    //   `What are the most effective methods to learn ${searchQuery}?`,
    //   `How can I learn ${searchQuery} effectively?`,
    //   `Top resources for learning ${searchQuery}`,
    //   `${searchQuery} for beginners: where to start?`,
    //   `Advanced techniques in ${searchQuery}`,
    //   `${searchQuery} vs other similar topics`,
    //   `Career opportunities with ${searchQuery} skills`,
    //   `Common mistakes when learning ${searchQuery}`,
    //   `How long does it take to master ${searchQuery}?`
    // ]
    setSearchResults(results)
  }

  return (
    <div className="w-full md:w-64 bg-gray-900 text-white flex flex-col h-full transition-all duration-300 ease-in-out fixed left-0 top-0 bottom-0 z-20">
      <div className="p-4 flex-grow overflow-hidden flex flex-col">
        <Button onClick={startNewConversation} className="mb-4">
          <PlusCircle className="mr-2 h-4 w-4" /> New Chat
        </Button>
        <ScrollArea className="flex-grow mb-4">
          {conversations.map((conversation) => (
            <div key={conversation.id} className="mb-2 flex items-center">
              <Button
                variant={conversation.id === currentConversation?.id ? "secondary" : "ghost"}
                className="w-full justify-start mr-2 text-left"
                onClick={() => setCurrentConversation(conversation)}
              >
                {conversation.title}
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Pencil className="h-4 w-4" />
                    <span className="sr-only">Edit</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <Dialog>
                    <DialogTrigger asChild>
                      <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                        Rename
                      </DropdownMenuItem>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Rename Conversation</DialogTitle>
                      </DialogHeader>
                      <Input
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        placeholder="Enter new title"
                      />
                      <DialogClose asChild>
                        <Button onClick={() => {
                          if (newTitle.trim() !== '') {
                            renameConversation(conversation.id, newTitle)
                            setNewTitle('')
                          }
                        }}>
                          Save
                        </Button>
                      </DialogClose>
                    </DialogContent>
                  </Dialog>
                  <DropdownMenuItem onSelect={() => deleteConversation(conversation.id)}>
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ))}
        </ScrollArea>
      </div>
      <div className="p-4 border-t border-gray-700">
        <form onSubmit={handleSearchSubmit} className="relative mb-2">
          <Input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-800 text-white placeholder-gray-400 border-gray-700"
          />
          <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" type='submit'>
            <Search />
          </button>
        </form>
        {searchResults.length > 0 && (
          <ScrollArea className="h-40 overflow-y-auto">
            <ul ref={searchResultsRef} className="space-y-1">
              {searchResults.map((result, index) => (
                <li key={index} className="relative text-sm text-gray-300 hover:bg-gray-800 p-1 rounded group">
                  <div className="relative z-0">{result}</div>
                  {searchState !== "error" && <div className="absolute z-10 top-0 bottom-0 right-0 hidden items-center group-hover:flex group-hover:bg-gray-800">
                    <TooltipProvider delayDuration={350} skipDelayDuration={150}>
                      <Tooltip>
                        <TooltipTrigger onClick={() => onPreprocessQuery(result, "append")}>
                          <PlusCircleIcon className="mr-1 rounded p-1 hover:text-white hover:bg-green-500 cursor-pointer"/>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">
                          Append
                        </TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger onClick={() => onPreprocessQuery(result, "replace")}>
                          <Replace className="rounded p-1 hover:text-white hover:bg-red-500 cursor-pointer"/>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">
                          Replace
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>}
                </li>
              ))}
            </ul>
          </ScrollArea>
        )}
        <Progress indeterminate className={"mt-2" + (searchState !== "loading" ? " bg-transparent [&_*]:bg-transparent" : "")} />
      </div>
    </div>
  )
}


