import os
import requests

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_BASE = "https://api.etherscan.io/api"

def get_tx_receipt_status(tx_hash):
    params = {
        "module": "transaction",
        "action": "gettxreceiptstatus",
        "txhash": tx_hash,
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(ETHERSCAN_API_BASE, params=params)
    response.raise_for_status()
    return response.json()

def verify_contract(
    contract_address,
    contract_name,
    compiler_version,
    source_code,
    code_format="solidity-single-file",
    chain_id="1",
    constructor_args=""
):
    data = {
        "module": "contract",
        "action": "verifysourcecode",
        "apikey": ETHERSCAN_API_KEY,
        "chainId": chain_id,
        "contractaddress": contract_address,
        "contractname": contract_name,
        "compilerversion": compiler_version,
        "sourceCode": source_code,
        "codeformat": code_format,
        "constructorArguments": constructor_args,
    }
    response = requests.post(ETHERSCAN_API_BASE, data=data)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    sample_tx_hash = "0x513c1ba0bebf66436b5fed86ab668452b7805593c05073eb2d51d3a52f480a76"
    try:
        result = get_tx_receipt_status(sample_tx_hash)
        print("Transaction receipt status result:", result)
    except Exception as e:
        print("Error fetching transaction receipt status:", e)

    contract_address = "0xYourContractAddress"
    contract_name = "contracts/Verified.sol:Verified"
    compiler_version = "v0.8.19+commit.7dd6d404"
    source_code = "pragma solidity ^0.8.19; contract Verified { }"
    try:
        verify_result = verify_contract(
            contract_address,
            contract_name,
            compiler_version,
            source_code
        )
        print("Contract verification result:", verify_result)
    except Exception as e:
        print("Error verifying contract:", e) 