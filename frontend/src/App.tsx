import { Routes, Route } from 'react-router-dom';

function App() {
    return (
        <Routes>
            <Route path="/" element={
              <div className="text-4xl font-bold">Hello there!</div>
            }/>
        </Routes>
    );
}

export default App;
