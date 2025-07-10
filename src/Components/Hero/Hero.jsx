import React from 'react'
import './Hero.css'

const Hero = () => {
  return (
    <div className='home-container'>
      
      <div className='hero-content'>
        <h1>Empowering Research <br></br>Across Africa</h1>
        <p className='intro'>Discover, share and showcase academic research from leading Africa Universities.</p>
        <p className='mission'><bold>Our mission is to create a unified academic platform where African students and researchers can easily publish, share and gain recognition for their academic work. We aim to foster collaboration, inspire innovation, and support the growth of knowledge across the continent</bold></p>
        <button>Submit Your Abstract</button>
      </div>
    </div>
  )
}

export default Hero
