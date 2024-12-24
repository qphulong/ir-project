import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage/page';
import NotFound from './pages/404';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<ChatPage/>}/>
                <Route path="*" element={<NotFound/>}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;