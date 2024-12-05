import { Routes, Route } from 'react-router-dom';
import  ChatPage from './pages/ChatPage/page';
function App() {
    return (
        <Routes>
            <Route path="/" element={
              <div className="text-4xl font-bold">Hello there!</div>
            }/>
            <Route path="/chat" element={
                <ChatPage/>
                }/>

        </Routes>
    );
}

export default App;
