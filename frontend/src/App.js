import React, { Component } from 'react';
import { BrowserRouter, Route } from 'react-router-dom';
import './App.css';

import Speakers from './Speakers';
import Speaker from './Speaker';

class App extends Component {
  render() {
    return (
      <BrowserRouter>
        <div className="App">
          <Route exact path="/" component={Speakers} />
          <Route path="/:speaker" component={Speaker} />
        </div>
      </BrowserRouter>
    );
  }
}

export default App;
