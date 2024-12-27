import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip'

interface InputAreaProps {
  onSendMessage: (content: string) => void
  preprocessedQuery: string | null
  disabled?: boolean
}

export function InputArea({ onSendMessage, preprocessedQuery, disabled }: InputAreaProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() === '') return
    onSendMessage(input)
    setInput('')
  }

  useEffect(() => {
    if (preprocessedQuery && !disabled) {
      setInput(preprocessedQuery)
    }
  }, [preprocessedQuery]);

  return (
    <form onSubmit={handleSubmit} className="h-full w-full pl-2 pr-4 py-4 border-t bg-white">
      <div className="flex space-x-2 h-full">
        <Textarea
          placeholder="Type your message here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-grow"
          rows={1}
          disabled={disabled}
        />
        <TooltipProvider delayDuration={350} skipDelayDuration={150}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button className="h-full" type="submit" disabled={disabled}>
                <Send />
                <span className="sr-only">Send</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              Send message
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </form>
  )
}

