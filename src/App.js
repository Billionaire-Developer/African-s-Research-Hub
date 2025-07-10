import './App.css'
import Navbar from './Components/Navbar/Navbar';
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import SubmitAbstract from './Pages/SubmitAbstract';
import Home from './Pages/Home'
import Payment from './Components/Payment/Payment';
import Student from './Components/Student/Student';
function App() {
  return (
    <div>
      <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path='/' element={<Home/>}/>
        <Route path='/Payment' element={<Payment/>}/>
        <Route path='/Abstract' element={<SubmitAbstract category="Abstract"/>}/>
        <Route path='/Student' element={<Student category="Student"/>}/>
      </Routes>

      </BrowserRouter>
    </div>
  );
}

export default App;
