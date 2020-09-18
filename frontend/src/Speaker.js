import React, { Component } from 'react';
import EventListener from 'react-event-listener';
import './Speaker.css';

class Speaker extends Component {
  constructor(props) {
    super();
    this.state = {
      uid: props.uid || null,
      name: props.name || "??",
      volume: props.volume || "??"
    };
    this.down = this.down.bind(this);
    this.up = this.up.bind(this);
    this.update = this.update.bind(this);
    this.timeout = null;
  }

  setVolume(newVolume) {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');
    let options = {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        volume: newVolume
      })
    };
    fetch('/api/v1/speakers/' + this.state.uid,
          options)
      .then(response => response.json())
      .then(json => this.setState({ volume: json.volume }));
  }

  down() {
    this.setVolume(this.state.volume - 1);
  }

  up() {
    this.setVolume(this.state.volume + 1);
  }

  update() {
    if (this.props.match && this.state.uid) {
      fetch('/api/v1/speakers/' + this.state.uid)
        .then(response => response.json())
        .then(json => this.setState({ volume: json.volume }));
      this.updateLater();
    }
  }

  updateLater() {
    if (this.timeout !== null)
      clearTimeout(this.timeout);
    this.timeout = setTimeout(this.update, 10000);
  }

  componentDidMount() {
    if (this.props.match) {
      const name_param = encodeURIComponent(this.props.match.params.speaker);
      fetch('/api/v1/speakers?name=' + name_param)
        .then(response => response.json())
        .then(json => {
          let best, best_ratio = -1;
          for (let speaker of json.speakers) {
            if (speaker.name_ratio > best_ratio) {
              best = speaker;
              best_ratio = speaker.name_ratio;
            }
          }
          this.setState({
            uid: best.uid,
            name: best.name,
            volume: best.volume
          });
          this.updateLater();
        });
    }
  }

  componentWillReceiveProps(newProps) {
    this.setState({
      volume: newProps.volume
    });
  }

  render() {
    if (!this.state.uid)
      return <div />;

    return (
      <div className="Speaker"
           onClick={this.update}>
        <EventListener
          target="document"
          onFocus={this.update}
        />
        <div className="Speaker-name">
          {this.state.name}
        </div>
        <div className="Speaker-volume">
          {this.state.volume}
        </div>
        <button className="Speaker-down"
                onClick={this.down}>-</button>
        <button className="Speaker-up"
                onClick={this.up}>+</button>
      </div>
    );
  }
}

export default Speaker;
