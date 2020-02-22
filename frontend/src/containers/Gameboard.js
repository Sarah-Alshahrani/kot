import React, { Component } from "react";
import "./Gameboard.css";
import config from "../services/config";

import GameConsole from "../components/GameConsole/GameConsole";
import DiceRoller from "./../components/Dice/DiceRoller";
import CardStore from "../components/Cards/CardStore";
import PlayerValuesDisplay from "./../components/PlayerValues/PlayerValueDisplay";

import GameInstance from "./../services/gameService";

export default class GameboardLayout extends Component {
  constructor(props) {
    super(props);

    let userName = "Guest_1234";
    let roomName = "Room_1234";
    if (props.location && props.location.state) {
      userName = props.location.state.username;
      roomName = props.location.state.gameRoom;
    }

    this.state = {
      username: userName,
      gameRoom: roomName,
      loggedIn: true
    };

    GameInstance.connect(this.state.gameRoom, config.GAME_SOCKET_API_PATH);
  }

  render() {
    return (
      <div className="board_container">
        <br />
        <h4>{this.state.gameRoom}</h4>
        <div>
          <div className="col">
            <CardStore
              currentUser={this.state.username}
              currentRoom={this.state.gameRoom}
            />
          </div>
        </div>
        <div className="container">
          {this.state.loggedIn ? (
            <div>
              <div className="row">
                <div className="col-sm">
                  <DiceRoller
                    currentUser={this.state.username}
                    currentRoom={this.state.gameRoom}
                  />
                </div>
                <div className="col-sm board_middle_column">
                  <GameConsole
                    sendMessage={payload => {
                      GameInstance.sendMessage(payload);
                    }}
                    currentUser={this.state.username}
                    currentRoom={this.state.gameRoom}
                  />
                </div>
                <div className="col-sm">
                  <PlayerValuesDisplay
                    currentUser={this.state.username}
                    currentRoom={this.state.gameRoom}
                    displayOnlySelf={true}
                  />
                </div>
              </div>
              <div className="row">
                <div className="col-sm">
                  <PlayerValuesDisplay
                    currentUser={this.state.username}
                    currentRoom={this.state.gameRoom}
                    displayOnlySelf={false}
                  />
                </div>
              </div>
            </div>
          ) : (
            <p>Please login</p>
          )}
        </div>
        <div className="col">
          <a href="https://icons8.com/">Images Provided by icons8.com</a>
        </div>
      </div>
    );
  }
}
