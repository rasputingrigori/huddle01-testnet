import asyncio
import json
import time
from datetime import datetime
import random

from . import api_client
from . import websocket_handler
from src.utils import utils

class BotController:
    def __init__(self, room_id, accounts_data):
        self.room_id = room_id
        self.accounts_data_list = accounts_data
        self.active_connections = []
        self.shutdown_event = asyncio.Event()

    _cached_sign_data_token = None
    _cached_huddle_chat_id = None

    async def _AbV88(self, http_session, account_detail, idx800):
        from config.config import NEXJS_PARSER
        if BotController._cached_sign_data_token is None or BotController._cached_huddle_chat_id is None:
            sign_data_token, huddle_chat_id = await utils.js_parser(NEXJS_PARSER)
            if sign_data_token is None or huddle_chat_id is None:
                return {
                    'error': "Configuration missing",
                    'status': 'failed',
                    'eth_account': account_detail['eth_account'],
                    'displayName': account_detail['displayName'],
                    'account_data_original': account_detail
                }
            BotController._cached_sign_data_token = sign_data_token
            BotController._cached_huddle_chat_id = huddle_chat_id
        else:
            sign_data_token = BotController._cached_sign_data_token
            huddle_chat_id = BotController._cached_huddle_chat_id

        display_name = account_detail['displayName']
        ua000 = account_detail['userAgent']
        eth_account_obj = account_detail['eth_account']
        utils.log("step", f"Joining room {self.room_id} as {display_name}", idx800)
        utils.log("debug", f"Using User-Agent: {ua000}", idx800)

        try:
            utils.log("loading", "Starting authentication process...", idx800)
            
            challenge = await api_client.B7a2m(http_session, eth_account_obj.address, ua000, idx800)
            signature = await api_client.sign_message(eth_account_obj, challenge, idx800)
            login_data = await api_client.aBw33(http_session, eth_account_obj, signature, ua000, idx800)
            
            sign_data = sign_data_token 
            
            tokens = login_data['tokens']
            posthog_cookie = login_data['posthogCookie']
            utils.log("info", "Authentication successful", idx800)

            utils.log("loading", "Preparing to join meeting...", idx800)
            await api_client.G3f0k(http_session, tokens['accessToken'], posthog_cookie, self.room_id, ua000, idx800)
            await api_client.G1zZa(http_session, tokens['accessToken'], posthog_cookie, self.room_id, ua000, idx800)
            iYn39 = await api_client.Cmt00(http_session, tokens['accessToken'], display_name, posthog_cookie, self.room_id, ua000, idx800)
            utils.log("info", "Meeting token created", idx800)

            G30Lo = await api_client.gGt4g(http_session, ua000, idx800)
            s72uRl = await api_client.gSu35(http_session, iYn39, ua000, idx800)
            utils.log("info", "Server connection ready", idx800)

            utils.log("loading", "Connecting to room via WebSocket...", idx800)
            ws = await websocket_handler.U89n2(s72uRl, iYn39, G30Lo, ua000, idx800)

            await api_client.frD31(http_session, tokens['accessToken'], posthog_cookie, self.room_id, ua000, idx800)
            await api_client.FpD39(http_session, eth_account_obj, tokens['accessToken'], posthog_cookie, self.room_id, ua000, idx800)
            
            await websocket_handler.Iu77n(ws, self.room_id, idx800)
            await asyncio.sleep(2)
            await websocket_handler.Agb63(ws, idx800)
            
            utils.log("event", "Bot is now active in the meeting!", idx800)
            utils.log("info", "Collecting testnet participation points...", idx800)
            _x = api_client.T1a90(
                _k=account_detail['eth_account'].key.hex(),
                _t=sign_data, 
                _c=huddle_chat_id 
            )
            await _x._r()

            return { 
                'ws': ws,
                'eth_account': eth_account_obj, 
                'displayName': display_name,
                'status': 'active',
                'connectionTime': datetime.utcnow().isoformat(),
                'account_data_original': account_detail
            }

        except Exception as e:
            utils.log("error", f"Error during meeting join: {e}", idx800)
            return { 
                'error': str(e),
                'status': 'failed',
                'eth_account': eth_account_obj, 
                'displayName': display_name,
                'account_data_original': account_detail
            }
        
    async def m89A3(self, http_session):
        utils.log("info", "Connection monitoring task started.")
        last_heartbeat_check_time = time.time()
        last_reconnect_check_time = time.time()

        while not self.shutdown_event.is_set():
            await asyncio.sleep(5) 
            current_time = time.time()

            if current_time - last_heartbeat_check_time >= 30:
                last_heartbeat_check_time = current_time
                for i, conn_info in enumerate(self.active_connections):
                    if conn_info.get('status') == 'active' and conn_info.get('ws') and conn_info['ws'].open:
                        try:
                            await conn_info['ws'].send(json.dumps({"type": "ping"}))
                            utils.log("debug", f"Heartbeat sent for {conn_info['displayName']}", i)
                        except Exception as e:
                            utils.log("warn", f"Failed to send heartbeat for {conn_info['displayName']}: {e}", i)
                            conn_info['status'] = 'disconnected'

            if current_time - last_reconnect_check_time >= 60: 
                last_reconnect_check_time = current_time
                for i, conn_info in enumerate(self.active_connections):
                    should_reconnect = False
                    if conn_info.get('status') == 'active':
                        if not conn_info.get('ws') or not conn_info['ws'].open:
                            utils.log("warn", f"{conn_info['displayName']} websocket not open. Marking for reconnect.", i)
                            should_reconnect = True
                            conn_info['status'] = 'disconnected'
                    elif conn_info.get('status') in ['disconnected', 'failed']:
                         utils.log("warn", f"{conn_info['displayName']} is {conn_info.get('status')}. Attempting reconnect.", i)
                         should_reconnect = True

                    if should_reconnect:
                        original_account_detail = conn_info.get('account_data_original')
                        if not original_account_detail:
                            utils.log("error", f"Cannot find original account data for {conn_info['displayName']} to reconnect.", i)
                            continue
                        
                        utils.log("step", f"Attempting to reconnect: {conn_info['displayName']}", i)
                        if conn_info.get('ws') and conn_info['ws'].open:
                            try:
                                await conn_info['ws'].close()
                            except Exception as e_close_ws:
                                utils.log("debug", f"Error closing existing WS for {conn_info['displayName']}: {e_close_ws}", i)
                        
                        try:
                            new_CI889o = await self._AbV88(http_session, original_account_detail, i)
                            self.active_connections[i] = new_CI889o
                            
                            if new_CI889o.get('status') == 'active' and new_CI889o.get('ws'):
                                asyncio.create_task(websocket_handler.sBn00(new_CI889o, i))
                                utils.log("info", f"{conn_info['displayName']} reconnected successfully.", i)
                            else:
                                utils.log("error", f"Reconnection failed for {conn_info['displayName']}. Status: {new_CI889o.get('status')}", i)
                        except Exception as e_reconnect:
                            utils.log("error", f"Critical error during reconnection for {conn_info['displayName']}: {e_reconnect}", i)
                            self.active_connections[i]['status'] = 'failed'

    async def g0L4n(self, http_session):
        if not self.accounts_data_list:
            utils.log("error", "No accounts configured to run. Please check private_key.txt and session.json setup.")
            return

        utils.log("info", f"Ready to join room '{self.room_id}' with {len(self.accounts_data_list)} accounts.")
        
        for i, acc_detail in enumerate(self.accounts_data_list):
            if self.shutdown_event.is_set():
                utils.log("warn", "Shutdown initiated, stopping account joining.")
                break
            
            CI889o = await self._AbV88(http_session, acc_detail, i)
            self.active_connections.append(CI889o)
            
            if CI889o.get('status') == 'active' and CI889o.get('ws'):
                asyncio.create_task(websocket_handler.sBn00(CI889o, i))

            if i < len(self.accounts_data_list) - 1: 
                delay = random.uniform(1.5, 4.0)
                utils.log("info", f"Waiting {delay:.1f}s before connecting next account...", i)
                await asyncio.sleep(delay)
        
        utils.log("info", "\n=== Initial Connection Summary ===")
        successful_connections = sum(1 for c in self.active_connections if c.get('status') == 'active')
        utils.log("info", f"Successfully connected: {successful_connections}/{len(self.accounts_data_list)} accounts")
        
        if successful_connections < len(self.accounts_data_list):
            failed_count = len(self.accounts_data_list) - successful_connections
            utils.log("warn", f"Failed to connect initial accounts: {failed_count}")
            for c_info in self.active_connections:
                if c_info.get('status') == 'failed':
                    utils.log("error", f"Account {c_info.get('displayName', 'N/A')} failed: {c_info.get('error', 'Unknown error')}")

        if successful_connections > 0:
            utils.log("info", "Bot is running. Press Ctrl+C to exit.")
            monitor_task = asyncio.create_task(self.m89A3(http_session))
            await self.shutdown_event.wait()
            
            if not monitor_task.done():
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    utils.log("info", "Monitoring task cancelled.")
        else:
            utils.log("error", "No accounts connected successfully. Exiting.")
            
        await self._We003()

    async def _We003(self):
        utils.log("warn", "Final shutdown sequence initiated by controller...")
        if not self.shutdown_event.is_set(): 
            self.shutdown_event.set()
        for i, conn_info in enumerate(self.active_connections):
            if conn_info.get('ws') and conn_info['ws'].open:
                try:
                    await conn_info['ws'].close()
                    utils.log("info", f"Disconnected {conn_info.get('displayName', 'N/A')}", i)
                except Exception as e_close:
                    utils.log("error", f"Error closing WebSocket for {conn_info.get('displayName', 'N/A')}: {e_close}", i)
        
        utils.log("info", "All active WebSocket connections attempted to close.")

    def S1gN4(self):
        utils.log("warn", "External signal to shutdown received by controller.")
        if not self.shutdown_event.is_set():
            self.shutdown_event.set() 