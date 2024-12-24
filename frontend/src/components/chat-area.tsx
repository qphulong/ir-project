import { ScrollArea } from "@/components/ui/scroll-area"
import { Message } from './chat-interface'
import { useEffect, useRef } from "react"
import { Info } from "lucide-react"


interface ChatAreaProps {
  messages: Message[]
  isTyping: boolean
}

export function ChatArea({ messages, isTyping }: ChatAreaProps) {
  const lastMessageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messages.length > 0 && lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages.length]);

  return (
    messages.length > 0 ? 
    <ScrollArea className="flex-grow p-4 space-y-4">
      {messages.map((message, index) => (
        <div
          key={message.id}
          className={`flex mb-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          ref={index === messages.length - 1 ? lastMessageRef : undefined}
        >
          <div
            className={`text-justify max-w-[70%] rounded-lg p-3 ${
              message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-800'
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}
      {isTyping && (
        <div className="flex justify-start">
          <div className="max-w-[70%] rounded-lg p-3 bg-gray-200 text-gray-800">
            <div className="typing-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </ScrollArea> :
    <div className="h-full flex flex-col gap-2 items-center justify-center text-center p-4 text-gray-500">
      <Info size={48}/>
      <p className="text-xl">No messages yet.</p>
  </div>
  )
}