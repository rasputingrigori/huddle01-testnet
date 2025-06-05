import json
import os
from faker import Faker
from eth_account import Account
from src.utils import utils
from config import config

class AccountManager:
    def __init__(self, private_key_file=config.PRIVATE_KEY_FILE, session_file=config.SESSION_FILE):
        self.private_key_file = private_key_file
        self.session_file = session_file
        self.faker = Faker()

    def _LpK32(self):
        private_keys = []
        if not os.path.exists(self.private_key_file):
            utils.log("error", f"{self.private_key_file} not found. Please create it and add private keys, one per line.")
            return private_keys
        
        try:
            with open(self.private_key_file, 'r') as f:
                for line in f:
                    pk = line.strip()
                    if pk and (pk.startswith('0x') or len(pk) == 64): 
                        private_keys.append(pk)
                    elif pk: 
                        utils.log("warn", f"Skipping invalid private key format in {self.private_key_file}: {pk[:10]}...")
            if not private_keys:
                utils.log("warn", f"{self.private_key_file} is empty or contains no valid keys.")
        except Exception as e:
            utils.log("error", f"Error reading {self.private_key_file}: {e}")
        return private_keys

    def _LsD43(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                utils.log("warn", f"Error decoding {self.session_file}. A new session file will be created.")
            except Exception as e:
                utils.log("error", f"Error reading {self.session_file}: {e}")
        return {}

    def _sSd00(self, session_data):
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=4)
            utils.log("info", f"Session data saved to {self.session_file}")
        except Exception as e:
            utils.log("error", f"Error writing to {self.session_file}: {e}")
            
    def _npK22(self, pk_string):
        if not pk_string.startswith('0x'):
            return '0x' + pk_string
        return pk_string

    def Ga33t(self, num_to_load):
        loaded_pks_str = self._LpK32()
        if not loaded_pks_str:
            return []

        session_data = self._LsD43()
        accounts_details = []
        updated_session = False

        if num_to_load == float('inf') or num_to_load >= len(loaded_pks_str):
            pks_to_process = loaded_pks_str
            num_requested_log = "all available" if num_to_load == float('inf') else num_to_load
        else:
            pks_to_process = loaded_pks_str[:int(num_to_load)]
            num_requested_log = int(num_to_load)
        
        utils.log("info", f"Processing {len(pks_to_process)} private keys (up to {num_requested_log} requested).")


        for pk_str_original in pks_to_process:
            pk_str_normalized = self._npK22(pk_str_original)
            try:
                eth_account_obj = Account.from_key(pk_str_normalized)
                address = eth_account_obj.address
                
                account_session_info = session_data.get(pk_str_normalized)

                if account_session_info and isinstance(account_session_info, dict) and \
                   account_session_info.get('displayName') and account_session_info.get('userAgent'):
                    display_name = account_session_info['displayName']
                    ua000 = account_session_info['userAgent']
                    utils.log("info", f"Loaded session for {address[:6]}...{address[-4:]}: Name='{display_name}'")
                else:
                    display_name = self.faker.user_name() 
                    ua000 = utils.generate_random_ua000()
                    session_data[pk_str_normalized] = {
                        'displayName': display_name,
                        'userAgent': ua000,
                        'address': address 
                    }
                    updated_session = True
                    utils.log("info", f"Generated new session for {address[:6]}...{address[-4:]}: Name='{display_name}'")

                accounts_details.append({
                    'privateKey': pk_str_normalized, 
                    'eth_account': eth_account_obj, 
                    'displayName': display_name,
                    'address': address,
                    'userAgent': ua000
                })

            except ValueError as ve: 
                utils.log("error", f"Invalid private key format encountered: {pk_str_original[:10]}... Error: {ve}")
            except Exception as e:
                utils.log("error", f"Error processing private key {pk_str_original[:10]}...: {e}")


        if updated_session:
            self._sSd00(session_data)
        
        return accounts_details
