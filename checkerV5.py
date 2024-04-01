# import threading
import os
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Optional
# from  etherscan import Etherscan
import requests
import json
from termcolor import colored, cprint
import logging, coloredlogs
from multiprocessing import Process
from multiprocessing import Pool
import multiprocessing
import time

# import time
# import os

from dotenv import load_dotenv

load_dotenv()

# Fixed Logs.
logging.basicConfig(handlers=[logging.FileHandler(filename="ErrorDump.log",
                                                  encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%F %A %T",
                    level=logging.WARNING)

ETHAPI = os.getenv('EHERSCAN_API')
BSCAPI = os.getenv('BSCSCAN_API')
TG_TOKEN = os.getenv('TG_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')
CPU_COUNT = 28


def send_message(token, chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f'Ошибка при отправке сообщения: { text }.')


# file = open('APIKeys.txt', 'a+')
#
# with open('APIKeys.txt', 'r') as f:
#     for line in f:
#         ETHAPI, BSCAPI = line.split(':')


def subforce():
    while True:
        MNEMONIC: str = generate_mnemonic(language="english", strength=128)
        PASSPHRASE: Optional[str] = None  # "meherett"
        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_mnemonic(
            mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE
        )
        bip44_hdwallet.clean_derivation()
        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=0)
        bip44_hdwallet.from_path(path=bip44_derivation)

        me = bip44_hdwallet.mnemonic()
        addr = bip44_hdwallet.address()
        logging.debug(f'{MNEMONIC} - {PASSPHRASE} - {bip44_hdwallet}')


        # #ETH
        try:
            eth = requests.get(
                f'https://api.etherscan.io/api?module=account&action=txlist&address={addr}&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey={ETHAPI}',
                timeout=5000.0)
        except requests.exceptions.RequestException as err:
            print(colored("Request Error", color="red"))
            logging.warning(err)

        try:
            ethJson = eth.json()
            dumpETHJson = json.dumps(ethJson)

            loadETHJson = json.loads(dumpETHJson)
            ethTransaction = loadETHJson["status"]

            # print(ethTransaction)
            if int(ethTransaction) > 0:

                send_message(TG_TOKEN, CHAT_ID, f"BSC CHAIN: {ethTransaction} -  {me} - {addr}")

                print(colored(f"Has transaction history - {me} - {addr}", color="green"))
                with open("valid.txt", "a") as ethWallets:
                    ethWallets.write("\nWallet: " + me + " ETH CHAIN " + addr)
            else:
                # send_message(TG_TOKEN, CHAT_ID, f"{ethTransaction} {me} {addr}")
                print(colored(f"ETH - {ethTransaction} - {addr}", color="yellow"))

                with open("empty.txt", "a") as ethWallets:
                    ethWallets.write("\nWallet: " + me + " ETH CHAIN " + addr)
        except Exception as e:
            print(e)

        # BSC
        try:
            bsc = requests.get(
                f'https://api.bscscan.com/api?module=account&action=txlist&address={addr}&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey={BSCAPI}',
                timeout=5000.0)
        except requests.exceptions.RequestException as err:
            print(colored("Requests Error", color="red"))
            logging.warning(err)

        try:
            bscJson = bsc.json()
            dumpBSCJson = json.dumps(bscJson)

            loadBSCJson = json.loads(dumpBSCJson)
            bscTransaction = loadBSCJson["status"]
            # print(colored("BSC", color="white"))
            # print(bscTransaction)
            if int(bscTransaction) > 0:

                send_message(TG_TOKEN, CHAT_ID, f"BSC CHAIN: {bscTransaction} -  {me} - {addr}")

                print(colored(f"Has transaction history {me} {addr}", color="green"))
                with open("valid.txt", "a") as bscWallets:
                    bscWallets.write("\nWallet: " + me + " BSC CHAIN " + addr)
            else:
                print(colored(f"BCS - {bscTransaction} - {addr}", color="yellow"))
                with open("empty.txt", "a") as ethWallets:
                    ethWallets.write("\nWallet: " + me + " BSC CHAIN " + addr)

            bip44_hdwallet.clean_derivation()

        except Exception as b:
            print(b)


def mainforce():
    print("Your ETH API key is: ")
    print(colored(f"{ETHAPI}", color="yellow"))
    print("Your bsc API key is: ")
    print(colored(f"{BSCAPI}", color="yellow"))

    print("Number of cpu : ", multiprocessing.cpu_count())
    # input a number
    while True:
        try:
            # TODO: Disable input waiting
            # num = int(input("Enter the number of multiprocesses that will perform the operation: "))
            num = CPU_COUNT
            break
        except ValueError:
            print("Please input integer only...")
            continue

    print("num:", num)
    print("Starting multiprocessing")

    for w in range(num):
        p = Process(target=subforce)
        p.start()
        time.sleep(0.1)

    print("Multiprocess started")


if __name__ == '__main__':
    mainforce()
