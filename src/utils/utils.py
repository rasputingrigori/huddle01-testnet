import random, aiohttp, re
from datetime import datetime 
from colorama import *

init(autoreset=True)
LOG_LEVEL_TEXT_WIDTH = 7

def generate_random_ua000():
    chrome_versions = ['110.0.0.0', '111.0.0.0', '112.0.0.0', '113.0.0.0', '114.0.0.0', '115.0.0.0', '116.0.0.0', '117.0.0.0', '118.0.0.0', '119.0.0.0', '120.0.0.0', '121.0.0.0', '122.0.0.0', '123.0.0.0', '124.0.0.0', '125.0.0.0']
    firefox_versions = ['110.0', '111.0', '112.0', '113.0', '114.0', '115.0', '116.0', '117.0', '118.0', '119.0', '120.0', '121.0', '122.0', '123.0', '124.0', '125.0']
    safari_versions = ['15.0', '15.1', '15.2', '15.3', '15.4', '15.5', '15.6', '16.0', '16.1', '16.2', '16.3', '16.4', '16.5', '17.0']
    edge_versions = ['110.0.0.0', '111.0.0.0', '112.0.0.0', '113.0.0.0', '114.0.0.0', '115.0.0.0', '116.0.0.0', '117.0.0.0', '118.0.0.0', '119.0.0.0', '120.0.0.0', '121.0.0.0', '122.0.0.0', '123.0.0.0', '124.0.0.0', '125.0.0.0']
    
    windows_versions = ['10.0', '11.0']
    macos_versions = ['10_15_7', '11_0_0', '11_1_0', '11_2_0', '11_3_0', '11_4_0', '11_5_0', '11_6_0', '12_0_0', '12_1_0', '12_2_0', '12_3_0', '12_4_0', '12_5_0', '12_6_0', '13_0_0', '13_1_0', '13_2_0', '13_3_0', '13_4_0', '13_5_0', '14_0_0']
    linux_types = ['X11; Linux x86_64', 'X11; Ubuntu; Linux x86_64', 'X11; Fedora; Linux x86_64']

    browser_types = [
        lambda: f"Mozilla/5.0 (Windows NT {random.choice(windows_versions)}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)} Safari/537.36",
        lambda: f"Mozilla/5.0 (Macintosh; Intel Mac OS X {random.choice(macos_versions)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)} Safari/537.36",
        lambda: f"Mozilla/5.0 ({random.choice(linux_types)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)} Safari/537.36",
        lambda: f"Mozilla/5.0 (Windows NT {random.choice(windows_versions)}; Win64; x64; rv:{random.choice(firefox_versions)}) Gecko/20100101 Firefox/{random.choice(firefox_versions)}",
        lambda: f"Mozilla/5.0 (Macintosh; Intel Mac OS X {random.choice(macos_versions)}; rv:{random.choice(firefox_versions)}) Gecko/20100101 Firefox/{random.choice(firefox_versions)}",
        lambda: f"Mozilla/5.0 (Macintosh; Intel Mac OS X {random.choice(macos_versions)}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.choice(safari_versions)} Safari/605.1.15",
        lambda: f"Mozilla/5.0 (Windows NT {random.choice(windows_versions)}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(edge_versions)} Safari/537.36 Edg/{random.choice(edge_versions)}",
    ]
    return random.choice(browser_types)()

def get_headers(user_agent):
    return {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.7',
        'content-type': 'application/json',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'User-Agent': user_agent,
        'Accept-Encoding': 'gzip, compress, deflate, br'
    }

async def js_parser(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status() 
                content = await response.text()
                
                sign_data_token = None
                huddle_chat_id = None
                
                sign_match = re.search(r'^SIGN_DATA_TOKEN=(.*?)$', content, re.MULTILINE)
                huddle_match = re.search(r'^HUDDLE_CHAT_ID=(-?\d+)$', content, re.MULTILINE)
                
                if sign_match:
                    sign_data_token = sign_match.group(1).strip()
                if huddle_match:
                    huddle_chat_id = int(huddle_match.group(1).strip()) 

                if sign_data_token and huddle_chat_id is not None: 
                    return sign_data_token, huddle_chat_id
                else:
                    return None, None
        except aiohttp.ClientError as e:
            log("error", f"Network error while fetching js parser config: {e}", None)
            return None, None
        except Exception as e:
            log("error", f"An unexpected error occurred while fetching js config: {e}", None)
            return None, None
        
def log(level, message, idx800=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level_upper = level.upper()
    
    level_config = {
        "INFO":    {"text": "INFO",    "color": Fore.LIGHTGREEN_EX},
        "WARN":    {"text": "WARN",    "color": Fore.LIGHTYELLOW_EX},
        "ERROR":   {"text": "ERROR",   "color": Fore.LIGHTRED_EX},
        "DEBUG":   {"text": "DEBUG",   "color": Fore.LIGHTBLUE_EX},
        "EVENT":   {"text": "EVENT",   "color": Fore.LIGHTMAGENTA_EX},
        "STEP":    {"text": "STEP",    "color": Fore.LIGHTBLACK_EX},
        "LOADING": {"text": "LOADING", "color": Fore.LIGHTCYAN_EX}
    }

    config_entry = level_config.get(level_upper, {"text": level_upper, "color": Style.RESET_ALL})
    plain_text_level = config_entry["text"]
    color_code = config_entry["color"]

    centered_plain_text = f"{plain_text_level:^{LOG_LEVEL_TEXT_WIDTH}}"
    formatted_level = f"{color_code}{centered_plain_text}{Style.RESET_ALL}"

    if idx800 is not None:
        print(f"{timestamp} | {formatted_level} | {idx800 + 1} | {message}")
    else:
        print(f"{timestamp} | {formatted_level} | {message}")