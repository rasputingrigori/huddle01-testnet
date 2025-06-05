import asyncio
import sys
import signal
import argparse
import re
import aiohttp
import os

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    from src.helpers.account_manager import AccountManager
    from src.helpers.main_controller import BotController
    from src.utils.utils import log
except ImportError as e:
    print(f"[ERROR] Failed to import huddle_bot modules: {e}")
    print("Ensure main.py is in the 'huddle_bot_project' directory, and 'huddle_bot' is a subdirectory.")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Sys.path: {sys.path}")
    sys.exit(1)

controller_instance = None

def signal_handler_fn(sig, frame):
    log("warn", f"Signal {signal.Signals(sig).name if hasattr(signal, 'Signals') else sig} received, initiating shutdown...")
    if controller_instance:
        controller_instance.S1gN4()
    else:
        log("error", "Controller not initialized for graceful shutdown via signal. Exiting.")
        sys.exit(1)

async def main_logic():
    global controller_instance
    
    parser = argparse.ArgumentParser(description="Huddle01 Testnet Bot")
    parser.add_argument("room_id", nargs='?', help="Huddle01 Room ID or full URL to join.")
    parser.add_argument("-n", "--num_accounts", type=int, default=0, 
                        help="Number of accounts to use from private_key.txt (0 for all).")
    
    args = parser.parse_args()
    room_id_input = args.room_id
    num_accounts_to_use = args.num_accounts

    if not room_id_input:
        while True:
            room_id_input = input("Enter the Huddle01 room ID to join: ").strip()
            if room_id_input:
                break
            log("error", "Room ID cannot be empty.")
    
    if 'huddle01.app/room/' in room_id_input:
        match = re.search(r'huddle01\.app/room/([^/?]+)', room_id_input)
        if match:
            room_id_input = match.group(1)
        else:
            log("error", f"Could not extract Room ID from URL: {room_id_input}")
            sys.exit(1)
    
    if num_accounts_to_use < 0:
        log("warn", "Number of accounts cannot be negative. Using all available accounts from private_key.txt.")
        num_accounts_to_use = 0 
    elif num_accounts_to_use == 0:
        log("info", "Using all available accounts from private_key.txt.")

    account_mgr = AccountManager()    
    accounts_data = account_mgr.Ga33t(num_to_load=float('inf') if num_accounts_to_use == 0 else num_accounts_to_use)

    if not accounts_data:
        log("error", "No accounts were loaded. Please check 'private_key.txt' and 'session.json' setup. Exiting.")
        sys.exit(1)
    
    if num_accounts_to_use > 0 and len(accounts_data) < num_accounts_to_use:
        log("warn", f"Requested {num_accounts_to_use} accounts, but only {len(accounts_data)} were available/loaded.")
    
    final_accounts_to_run_with = accounts_data 
    controller_instance = BotController(room_id=room_id_input, accounts_data=final_accounts_to_run_with)

    loop = asyncio.get_running_loop()
    for sig_name_enum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig_name_enum, lambda s=sig_name_enum: signal_handler_fn(s, None))
        except (NotImplementedError, AttributeError, RuntimeError):
            log("warn", f"loop.add_signal_handler not available for {signal.Signals(sig_name_enum).name if hasattr(signal, 'Signals') else sig_name_enum}. Using signal.signal().")
            signal.signal(sig_name_enum, signal_handler_fn)

    connector = aiohttp.TCPConnector(limit_per_host=25, ssl=False) 
    async with aiohttp.ClientSession(connector=connector) as http_session:
        try:
            await controller_instance.g0L4n(http_session)
        except asyncio.CancelledError:
            log("warn", "Main execution task was cancelled.")
        except Exception as e:
            log("error", f"An unhandled error occurred in main execution: {e}")

        finally:
            log("info", "Main execution finished or was interrupted. Initiating final cleanup.")
            if controller_instance and not controller_instance.shutdown_event.is_set():
                controller_instance.S1gN4() 
                await controller_instance.shutdown_event.wait() 

            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            if tasks:
                log("warn", f"Cancelling {len(tasks)} remaining outstanding tasks...")
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
            log("info", "Application shutdown complete.")

if __name__ == '__main__':
    from src.utils import banner 
    for sig_name_enum_main in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig_name_enum_main, signal_handler_fn)
    
    try:
        print("\033[H\033[J")
        banner.s0x000()
        asyncio.run(main_logic())
    except KeyboardInterrupt:
        log("warn", "\nKeyboardInterrupt caught at top level. Application will exit.")
    except SystemExit as se: 
        if se.code != 0:
             log("error", f"Application exited with code {se.code}")
    except Exception as e_top:
        log("error", f"Top-level unhandled exception: {e_top}")
