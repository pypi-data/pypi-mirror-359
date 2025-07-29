# 💲Stash💲
### The CLI tool for recording all your money related transactions!
---

## 💡Key Features

#### `init`

Initialize the tool by specifying the file path where the data will be stored (in a JSON file). Also set a currency for the accounts.

#### `accounts`
`add` - Add a new account.

`delete` - Delete an existing account.

`summary` - Get details like account holder's **Name**, **Email**, **DOB**, **ID**, **Total Balance** of an existing account.

`statement` - Get the pretty printed tabular format of the transaction of an existing account.

#### `transactions`
`credit` - Add a **credit** transaction to an existing account by providing the account's **ID**, **Credit Amount**, **description**.

`debit` - Add a **debit** transaction to an existing account by providing the account's **ID**, **Debit Amount**, **description**.

`delete` - Delete a transaction from an account by providing the account's **ID** and the **Transaction ID**.

## ⌨️Usage Examples

`stash init D:\stash_data --file_name "stash_db.json --currency €`

This initializes the stash CLI. It is important to initialize the tool before first use. This command will store all
accounts and related data in **stash_db.json** file and the currency will be set to €. This currency is set for all
accounts on Stash. Currently, it is not possible to set individual currencies for accounts.

`stash accounts add "John Doe" "johndoe@gmail.com" 1980-05-01`

This creates an account with the Account holder name as **John Doe**, the email address as **johndoe@gmail.com** and John's DOB as **01-05-1980**. A Unqiue ID is also created for this account. It follows the pattern firstnamelastname_dob. In this example, the Unique ID will be **johndoe_151980**.

`stash accounts summary`

Displays all the accounts on Stash with all details of each account and the account balance.

`stash transactions credit johndoe_151980 1000 --desc "Initial transaction"`

This creates a CREDIT transaction and adds money to John's account. A transaction ID is created (UNIX timestamp). The Date, time, description, type and amount is recorded in every transaction. A Similar command can be used for DEBIT where the money is removed from an account.

`stash accounts statement johndoe_151980`

This displays all the transactions for John's account. All columns mentioned above for the credit example are all displayed in a neat table format.

`stash transactions delete johndoe_151980 1751128581`

This removes a transaction from John's account which has a unique ID **1751128581**. Balance for the account is updated accordingly.

## 📸 CLI Screenshots
![image](https://github.com/user-attachments/assets/4c77b39a-f97d-4f35-922b-bc96b56e2844)

![image](https://github.com/user-attachments/assets/567c9067-0802-4557-8072-4df219e6c8f0)

![image](https://github.com/user-attachments/assets/b02d65bc-6630-451d-ad4d-b9b192810b89)

![image](https://github.com/user-attachments/assets/bab647d5-109f-45bc-9de9-262c49d73c09)


## 🔗Dependencies

python, click, tabular





