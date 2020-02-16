import json
import pickle

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from game.dice.dice_resolver import dice_resolution
from game.engine.board import BoardGame
from game.engine.dice_msg_translator import decode_selected_dice_indexes, dice_values_message_create
from game.models import User, GameState
from game.player.player import Player
from game.player.player_status_resolver import player_status_summary_to_JSON
from game.values.constants import DEFAULT_DICE_TO_ROLL, DEFAULT_RE_ROLL_COUNT
from lobby.server_message_types import PLAYER_STATUS_UPDATE_RESPONSE, BEGIN_TURN_RESPONSE, SERVER_RESPONSE, \
    DICE_ROLLS_RESPONSE, CARD_STORE_RESPONSE


def reconstruct_game(data):
    username = data['user']
    room = data['room']

    game = GameState.objects.get(room_name=room)
    # deserialize then store GameState object
    state: BoardGame = pickle.loads(game.board)
    return username, room, game, state


def save_game(game, state):
    game.board = pickle.dumps(state)
    game.save()


def create_send_response_to_client(command, username, room, payload):
    content = {
        'command': command,
        'action': {
            'user': username,
            'room': room,
            'content': payload
        }
    }
    return content


class GameConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'kot_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # leave group room
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_group_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'group_message',
                'message': message
            }
        )

    # Receive message from room group
    def group_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

    def send_to_client(self, message_type, username, room, payload):
        content = create_send_response_to_client(message_type, username, room, payload)
        self.send_group_message(content)

    def get_or_create_user(self, username, room):
        user, created = User.objects.get_or_create(username=username)

        if not user:
            error = 'Unable to get or create User with username: ' + username
            self.send_to_client(SERVER_RESPONSE, username, room, error)

        success = 'Chatting in with success with username: ' + username
        self.send_to_client(SERVER_RESPONSE, username, room, success)
        return user

    def get_or_create_game(self, username, room):
        game, created = GameState.objects.get_or_create(room_name=room)

        if not game:
            error = 'Unable to get or create Game with room: ' + room
            self.send_to_client(SERVER_RESPONSE, username, room, error)

        success = 'Chatting in with success within room: ' + room
        self.send_to_client(SERVER_RESPONSE, username, room, success)
        return game

    def start_web_game(self, room, state, username):
        state.start_game()
        self.send_to_client(SERVER_RESPONSE, username, room, "Game started..")
        state.dice_handler.roll_initial(DEFAULT_DICE_TO_ROLL, DEFAULT_RE_ROLL_COUNT)
        self.send_to_client(CARD_STORE_RESPONSE, username, room, state.deck_handler.json_store())
        self.send_to_client(BEGIN_TURN_RESPONSE, username, room, state.players.get_current_player().username)
        print("Game started..")

    def init_chat_handler(self, data):
        username = data['user']
        room = data['room']

        self.get_or_create_game(username, room)

        game = GameState.objects.get(room_name=room)
        if not game.board:
            state = BoardGame()
        else:
            state = pickle.loads(game.board)

        player: Player = Player(username)
        if player not in state.players.players:
            state.add_player(player)

        # hack to start game after 2 players join
        temp_max_players = 2
        if len(state.players.players) == temp_max_players:
            self.start_web_game(room, state, username)
        else:
            msg = "Joined, waiting on additional players"
            self.send_to_client(SERVER_RESPONSE, username, room, username + msg)

        player_summaries = player_status_summary_to_JSON(state.players)
        self.send_to_client(PLAYER_STATUS_UPDATE_RESPONSE, username, room, player_summaries)

        save_game(game, state)

    def return_dice_state_handler(self, data):
        username, room, game, state = reconstruct_game(data)

        values = state.dice_handler.dice_values
        rolled_dice_ui_message = dice_values_message_create(values)

        self.send_to_client(DICE_ROLLS_RESPONSE, username, room, rolled_dice_ui_message)

    def selected_dice_handler(self, data):
        username, room, game, state = reconstruct_game(data)

        payload = data['payload']

        selected_dice = decode_selected_dice_indexes(payload)

        try:
            state.dice_handler.re_roll_dice(selected_dice)
        except ValueError:
            self.send_to_client(SERVER_RESPONSE, username, room, "{} out of rolls.".format(username))

        # serialize then store modified GameState object
        save_game(game, state)

        values = state.dice_handler.dice_values
        rolled_dice_ui_message = dice_values_message_create(values)
        self.send_to_client(DICE_ROLLS_RESPONSE, username, room, rolled_dice_ui_message)

    def end_turn_handler(self, data):
        # a method to end a players turn and let the next guy go
        username, room, game, state = reconstruct_game(data)

        # TODO move to somewhere else
        dice_resolution(state.dice_handler.dice_values, state.players.get_current_player(),
                        state.players.get_all_alive_players_minus_current_player())
        self.send_to_client(SERVER_RESPONSE, username, room, "{} now has {} energy".format(username,
                                                                                           state.players.current_player.energy))

        cur_player = state.players.current_player
        print("Current player now has {} energy, {} health, and {} victory points".format(cur_player.energy,
                                                                                          cur_player.current_health,
                                                                                          cur_player.victory_points))

        player_summaries = player_status_summary_to_JSON(state.players)
        self.send_to_client(PLAYER_STATUS_UPDATE_RESPONSE, username, room, player_summaries)

        next_player: Player = state.get_next_player_turn()

        state.dice_handler.roll_initial(DEFAULT_DICE_TO_ROLL, DEFAULT_RE_ROLL_COUNT)

        values = state.dice_handler.dice_values
        rolled_dice_ui_message = dice_values_message_create(values)

        save_game(game, state)

        if next_player is not None:
            self.send_to_client(BEGIN_TURN_RESPONSE, username, room, next_player.username)
        else:
            self.send_to_client(BEGIN_TURN_RESPONSE, username, room, "None")

        self.send_to_client(DICE_ROLLS_RESPONSE, next_player.username, room, rolled_dice_ui_message)

    def gamelog_send_handler(self, data):
        username, room, game, state = reconstruct_game(data)

        mud_gamelog_input = data['payload']

        self.send_to_client(SERVER_RESPONSE, username, room, mud_gamelog_input)

    def card_store_request_handler(self, data):
        username, room, game, state = reconstruct_game(data)
        selected_cards_ui_message = state.deck_handler.json_store()

        self.send_to_client(CARD_STORE_RESPONSE, username, room, selected_cards_ui_message)

    commands = {
        'init_user_request': init_chat_handler,
        'gamelog_send_request': gamelog_send_handler,
        'selected_dice_request': selected_dice_handler,
        # 'roll_dice_request': roll_dice_handler,
        'return_dice_state_request': return_dice_state_handler,
        'end_turn_request': end_turn_handler,
        'card_store_request': card_store_request_handler
    }
