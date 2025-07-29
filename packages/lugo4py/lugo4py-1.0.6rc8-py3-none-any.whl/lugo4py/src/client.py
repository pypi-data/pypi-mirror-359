import grpc
import time
from concurrent.futures import ThreadPoolExecutor
import traceback
from typing import Callable, Iterator
from typing import List

from .game_snapshot_inspector import GameSnapshotInspector

from ..protos.server_pb2 import GameSnapshot, Order, OrderSet, JoinRequest
from ..protos import server_pb2_grpc as server_grpc
from ..protos.physics_pb2 import Point

from .interface import Bot
from .define_state import PLAYER_STATE, define_state
from .loader import EnvVarLoader
import threading

PROTOCOL_VERSION = "1.0.0"

RawTurnProcessor = Callable[[GameSnapshotInspector], List[Order]]


# reference https://chromium.googlesource.com/external/github.com/grpc/grpc/+/master/examples/python/async_streaming/client.py
class LugoClient(server_grpc.GameServicer):

    def __init__(self, server_add, grpc_insecure, token, teamSide, number, init_position):
        self._client = None
        self.getting_ready_handler = lambda snapshot: None
        self.callback = RawTurnProcessor
        self.serverAdd = server_add + "?t=" + str(teamSide) + "-" + str(number)
        self.grpc_insecure = grpc_insecure
        self.token = token
        self.teamSide = teamSide
        self.number = number
        self.init_position = init_position
        self._play_finished = threading.Event()
        self._play_routine = None

    def set_client(self, client: server_grpc.GameStub):
        self._client = client

    def get_name(self):
        return f"{'HOME' if self.teamSide == 0 else 'AWAY'}-{self.number}"

    def set_initial_position(self, initial_position: Point):
        self.init_position = initial_position

    def getting_ready_handler(self, inspector: GameSnapshotInspector):
        print(f'Default getting ready handler called for ')

    def set_ready_handler(self, new_ready_handler):
        self.getting_ready_handler = new_ready_handler

    def play(self, executor: ThreadPoolExecutor, callback: Callable[[GameSnapshot], OrderSet],
             on_join: Callable[[], None]) -> threading.Event:
        self.callback = callback
        log_with_time(f"{self.get_name()} Starting to play")
        return self._bot_start(executor, callback, on_join)

    def play_as_bot(self, executor: ThreadPoolExecutor, bot: Bot, on_join: Callable[[], None]) -> threading.Event:
        self.set_ready_handler(bot.getting_ready)
        log_with_time(f"{self.get_name()} Playing as bot")

        def processor(inspector: GameSnapshotInspector)  -> List[Order]:
            player_state = define_state(
                inspector, self.number, self.teamSide)
            if self.number == 1:
                orders = bot.as_goalkeeper(inspector, player_state)
            else:
                if player_state == PLAYER_STATE.DISPUTING_THE_BALL:
                    orders = bot.on_disputing(inspector)
                elif player_state == PLAYER_STATE.DEFENDING:
                    orders = bot.on_defending(inspector)
                elif player_state == PLAYER_STATE.SUPPORTING:
                    orders = bot.on_supporting(inspector)
                elif player_state == PLAYER_STATE.HOLDING_THE_BALL:
                    orders = bot.on_holding(inspector)
            return orders

        return self._bot_start(executor, processor, on_join)

    def _bot_start(self, executor: ThreadPoolExecutor, processor: RawTurnProcessor,
                   on_join: Callable[[], None]) -> threading.Event:
        log_with_time(f"{self.get_name()} Starting bot {self.teamSide}-{self.number}")
        if self.grpc_insecure:
            channel = grpc.insecure_channel(self.serverAdd)
        else:
            channel = grpc.secure_channel(
                self.serverAdd, grpc.ssl_channel_credentials())
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
        except grpc.FutureTimeoutError:
            raise Exception(f"timed out waiting to connect to the game server ({self.serverAdd})")

        self.channel = channel
        self._client = server_grpc.GameStub(channel)

        join_request = JoinRequest(
            token=self.token,
            team_side=self.teamSide,
            number=self.number,
            init_position=self.init_position,
        )

        response_iterator = self._client.JoinATeam(join_request)
        on_join()
        self._play_routine = executor.submit(self._response_watcher, response_iterator, processor)
        return self._play_finished

    def stop(self):
        log_with_time(
            f"{self.get_name()} stopping bot - you may need to kill the process if there is no messages coming from "
            f"the server")
        self._play_routine.cancel()
        self._play_finished.set()
        exit(0)

    def wait(self):
        self._play_finished.wait(timeout=None)

    def _response_watcher(
            self,
            response_iterator: Iterator[GameSnapshot],
            # snapshot,
            processor: RawTurnProcessor) -> None:
        try:
            for snapshot in response_iterator:
                inspector =  GameSnapshotInspector(self.teamSide, self.number, snapshot)
                if snapshot.state == GameSnapshot.State.OVER:
                    log_with_time(
                        f"{self.get_name()} All done! {GameSnapshot.State.OVER}")
                    break
                elif self._play_finished.is_set():
                    break
                elif snapshot.state == GameSnapshot.State.LISTENING:
                    orders : List[Order] = []
                    try:
                        orders = processor(inspector)
                    except Exception as e:
                        traceback.print_exc()
                        log_with_time(f"{self.get_name()}bot processor error: {e}")

                    if orders and len(orders) > 0:
                        order_set = OrderSet()
                        order_set.turn = inspector.get_turn()
                        order_set.orders.extend(orders)
                        self._client.SendOrders(order_set)
                    else:
                        log_with_time(
                            f"{self.get_name()} [turn #{snapshot.turn}] bot {self.teamSide}-{self.number} did not return orders")
                elif snapshot.state == GameSnapshot.State.GET_READY:
                    self.getting_ready_handler(snapshot)

            self._play_finished.set()
        except grpc.RpcError as e:
            if grpc.StatusCode.INVALID_ARGUMENT == e.code():
                log_with_time(f"{self.get_name()} did not connect {e.details()}")
        except Exception as e:
            log_with_time(f"{self.get_name()} internal error processing turn: {e}")
            traceback.print_exc()


def NewClientFromConfig(config: EnvVarLoader, initialPosition: Point) -> LugoClient:
    return LugoClient(
        config.get_grpc_url(),
        config.get_grpc_insecure(),
        config.get_bot_token(),
        config.get_bot_team_side(),
        config.get_bot_number(),
        initialPosition,
    )


def log_with_time(msg):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"{current_time}: {msg}")
