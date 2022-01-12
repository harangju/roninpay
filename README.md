# roninpay

RoninPay is a script to automate `$SLP` payments.

### Setup

#### Requirements
1. [anaconda](https://www.anaconda.com/products/individual) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) (more light weight)
2. Microsoft Excel (will update with version that uses a csv file)

##### Mac
1. Download this repository. Either `Open with GitHub Desktop` or `Download ZIP`. <img width="574" alt="Screen Shot 2022-01-12 at 18 25 06" src="https://user-images.githubusercontent.com/3681455/149239026-016f016e-60ff-467b-bdb3-53463b78c1ea.png">
2. Open a `Terminal` app. <img width="338" alt="Screen Shot 2022-01-12 at 18 31 26" src="https://user-images.githubusercontent.com/3681455/149239598-d7432d9a-d1b5-4756-8316-f828811064d4.png">
3. `cd` to the downloaded folder. Ex) `cd ~/Developer/roninpay` 
4. `conda env create -f environment.yml`
5. Now you are ready for payments!

##### Windows
Pending... should work with [anaconda](https://www.anaconda.com/products/individual) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) (more light weight).

### Payments

##### Mac
1. Fill in the `payments.xlsx` file with the necessary information. 
    - NOTE: Multiple payments from the same address are executed with a few minutes in between each transaction so that transactions have time to be included in blocks before submitting another transaction from the same address.
    - WARNING: You must write your private keys in the `payments.xlsx` file. I recommend that you make a temporary address, send only the $SLP you need for the payments to that address, and use that address to send out payments. Further, you should test with a small amount to make sure that you know how to use the code.
3. Run `./payout.sh` in this directory.

### Disclaimer

**Use this code at your own risk**: None of contributors or anyone else connected with this code, in any way whatsoever, can be responsible for your use of the code in this repository.
