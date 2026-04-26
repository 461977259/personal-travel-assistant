import { HashRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Wardrobe from './pages/Wardrobe';
import Outfit from './pages/Outfit';
import Trip from './pages/Trip';
import Content from './pages/Content';
import './styles/global.css';

function App() {
  return (
    <HashRouter>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/wardrobe" element={<Wardrobe />} />
            <Route path="/outfit" element={<Outfit />} />
            <Route path="/trip" element={<Trip />} />
            <Route path="/content" element={<Content />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}

export default App;
