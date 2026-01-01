import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';

function App() {
  const [showSupport, setShowSupport] = useState(false);

  // This method will set showSupport flag as True which was initialized as False at start of code
  const handleSupportClick = () => {
    setShowSupport(true)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">HK Voice Agent</div> 
      </header>

      <main>
        <section className="hero">
          <h1>Intelligent Real time support</h1>
          {/*
          <p>Free Next Day Delivery on Eligible Orders</p>
          <div className="search-bar">
            <input type="text" placeholder='Enter vehicle or part number'></input>
            <button>Search</button>
          </div>
          */}
        </section>
        {/* This button when pressed will invoke handleSupportClick function */}
        <button className="support-button" onClick={handleSupportClick}>  
          Talk to Friday!
        </button>
      </main>
      {/* This code will invoke LiveKitModal.jsx */}
      {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
    </div>
  )
}

export default App