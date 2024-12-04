import { ScrollArea } from "@/components/ui/scroll-area"
import { Message } from './chat-interface'

interface ChatAreaProps {
  messages: Message[]
}

export function ChatArea({ messages }: ChatAreaProps) {
  return (
    <ScrollArea className="flex-grow p-4 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg p-3 ${
              message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-800'
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}
    </ScrollArea>
  )
}

