import React, { Component } from 'react';
import './Speakers.css';

import Speaker from './Speaker';

class Speakers extends Component {
  constructor() {
    super();
    this.state = { speakers: [] };
    this.update = this.update.bind(this);
    this.timeout = null;
  }

  update() {
    fetch('/api/v1/speakers')
      .then(response => response.json())
      .then(json => this.setState(json));
    if (this.timeout !== null)
      clearTimeout(this.timeout);
    this.timeout = setTimeout(this.update, 10000);
  }

  componentDidMount() {
    this.update();
  }

  render() {
    let speakers = [];
    for (let speaker of this.state.speakers) {
      speakers.push(
        <Speaker key={speaker.uid}
                 uid={speaker.uid}
                 name={speaker.name}
                 volume={speaker.volume} />
      );
    }
    return (
      <div className="Speakers"
           onClick={this.update}>
        {speakers}
      </div>
    );
  }
}

export default Speakers;
