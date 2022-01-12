from collections import namedtuple
from datetime import datetime
from web3 import Web3
import json, math, os, sys, time

import slp_utils

RONIN_ADDRESS_PREFIX = "ronin:"

# Data types
Transaction = namedtuple("Transaction", "from_address to_address amount")
Payment = namedtuple("payment", "name private_key slp_balance account_address nonce transaction")

def parseRoninAddress(address):
  assert(address.startswith(RONIN_ADDRESS_PREFIX))
  return Web3.toChecksumAddress(address.replace(RONIN_ADDRESS_PREFIX, "0x"))

def formatRoninAddress(address):
  return address.replace("0x", RONIN_ADDRESS_PREFIX)

def log(message="", end="\n"):
  print(message, end = end, flush=True)
  sys.stdout = log_file
  print(message, end = end) # print to log file
  sys.stdout = original_stdout # reset to original stdout
  log_file.flush()

def wait(seconds):
  for i in range(0, seconds):
    time.sleep(1)
    log(".", end="")
  log()

today = datetime.now()
log_path = f"logs/logs-{today.year}-{today.month:02}-{today.day:02}.txt"

if not os.path.exists(os.path.dirname(log_path)):
  os.makedirs(os.path.dirname(log_path))
log_file = open(log_path, "a", encoding="utf-8")
original_stdout = sys.stdout

log(f"*** Welcome to the SLP Payment script *** ({today})")

# Load rows data.
# if (len(sys.argv) != 2):
#   log("Please specify the path to the json config file as parameter.")
#   exit()

# with open(sys.argv[1]) as f:
log("Generating payments...")
with open('slp-payment-config.json') as f:
  rows = json.load(f)

nonces = {} # actual
nonce_counts = {} # predicted
for payment in rows:
  address = parseRoninAddress(payment['From'])
  nonces[address] = slp_utils.web3.eth.get_transaction_count(address)
  nonce_counts[address] = nonces[address]

payments = {}
for payment in rows:
  name = payment["Name"]
  from_address = parseRoninAddress(payment["From"])
  to_address = parseRoninAddress(payment["To"])
  slp_balance = slp_utils.get_claimed_slp(from_address)

  if (slp_balance == 0):
    log(f"Skipping account '{name}' ({formatRoninAddress(from_address)}) because SLP balance is zero.")
    continue

  if nonce_counts[from_address]==nonces[from_address]:
    nonce = nonces[from_address]
  else:
    nonce = nonce_counts[from_address]
  nonce_counts[from_address] += 1

  if from_address not in payments:
    payments[from_address] = []

  payments[from_address].append(Payment(
    name = name,
    private_key = payment["PrivateKey"],
    slp_balance = int(payment['Amount']),
    account_address = from_address,
    nonce = nonce,
    transaction = Transaction(from_address = from_address, to_address = to_address, amount = int(payment['Amount']))
  ))

if (len(payments) == 0):
  log("\nNo payments to make!")
  exit()

log("\nPlease review the payments:")
time.sleep(1)
for name, ps in payments.items():
  log(f"\nPayment from '{name}'")
  for payment in ps:
    log(f"├─ Nonce: {payment.nonce}")
    log(f"│  SLP amount: {payment.slp_balance} SLP")
    log(f"│  From: {formatRoninAddress(payment.transaction.from_address)}")
    log(f"│  To: {formatRoninAddress(payment.transaction.to_address)}\n")

log("\nWould you like to execute payment (y/n) ?", end=" ")
if (input() != "y"):
  exit()

while len([payment for ps in payments.values() for payment in ps]) > 0:
  log("Executing payments...\n")
  for name, ps in payments.items():
    if len(ps)==0:
      continue
    log(f"Executing payment for '{name}'")
    payment = ps[0]
    if (nonces[payment.account_address] == payment.nonce):
      log(f"├─ Payment: sending {payment.transaction.amount} SLP from {formatRoninAddress(payment.transaction.from_address)} to {formatRoninAddress(payment.transaction.to_address)}...")
      try:
        hash = slp_utils.transfer_slp(payment.transaction, payment.private_key, payment.nonce)
        log(f"│  Hash: {hash}")
        log(f"│  Link: https://explorer.roninchain.com/tx/{str(hash)}\n")
      except Exception as e:
        log(f"WARNING: " + str(e))
        time.sleep(0.250)
    else:
      log(f"├─ Payment skipped because it has succeeded already.\n")

  minutes_to_wait = 1
  seconds_to_wait = int(minutes_to_wait*60)
  total_num_dots = 20
  log(f"Waiting {minutes_to_wait} minutes to give time to new blocks to be mined.", end="")
  for i in range(seconds_to_wait): #seconds
    if i % int(seconds_to_wait / total_num_dots + 1) == 0:
      log('.', end='')
    time.sleep(1)
  log()

  log("Detecting payments that failed...")
  completed_payments = []
  for name, ps in payments.items():
    if len(ps)==0:
     continue
    payment = ps[0]
    expected_nonce = payment.nonce + 1
    actual_nonce = nonces[payment.account_address] = slp_utils.web3.eth.get_transaction_count(payment.account_address)

  if (actual_nonce == expected_nonce):
    if len(payments[name]) > 0:
      payments[name].pop(0)
  else:
    log(f"Payment for '{payment.name}' didn't succeeded completely.")
    log(f"Expected nonce: {expected_nonce}. Actual nonce: {actual_nonce}")
    log(f"Will try payment again for '{payment.name}' at nonce {expected_nonce}.")

  total_payments = [payment for ps in payments.values() for payment in ps]
  if len(total_payments) == 0:
    log("All payments completed successfully!")

log()
log("Program completed. Have a nice day!")
