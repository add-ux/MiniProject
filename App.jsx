// App.jsx
import './App.css';
import LandingPage from './components/LandingPage';
import Signup from "./components/signup";
import Login from "./components/login";
import AnalyzePage from "./components/analyzepage";
import '@fortawesome/fontawesome-free/css/all.min.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/analyze" element={<AnalyzePage />} />
      </Routes>
    </Router>
  );
}

export default App;