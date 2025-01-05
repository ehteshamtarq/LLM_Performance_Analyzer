import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/home/home'
import DatasetDetails from './components/DatasetDetails/DatasetDetails'
import ResultPage from './components/resultPage/resultPage';

function App() {

  return (
    <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dataset/:id" element={<DatasetDetails/>} /> 
          <Route path="/result/dataset/:dataset_id/prompt/:prompt_id" element={<ResultPage/>} />
        </Routes>
    </Router>
  )
}

export default App
