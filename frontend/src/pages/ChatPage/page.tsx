import { Toaster } from '@/components/ui/toaster';
import ChatInterface from '../../components/chat-interface'
// import chatPage.css

import "./chatPage.css"


export default function ChatPage() {
  return (
    <>
      <ChatInterface />
      <Toaster />
    </>
  );
}

