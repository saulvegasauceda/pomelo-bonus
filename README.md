# Bonus Pomelo Coding Project:

I made a simple UI to view the summary of the results with two tables displaying the pending and settled transactions, as well as a banner with the available credit and payable balance. I also created an API connected to a SQL DB keeping track of pending and settled transactions.

## Additional functionality
I included a way for users to "Make Payments" which will randomly generate a `txnId` and initiate a payment. I did not enable for users via the front-end to POST settle or posted transactions since that's not typically how banks run their business.

## How to use:
In `pomelo-py`:
    run `python send_data.py` # this initializes the table with some data
    run `python pomelo_api.py` # this runs the API

In `pomelo-ts`:
    run `npm start` # should open interface

## Thoughts and Misc.
Most of the logic is in `pomelo-py/account.py`. This is where I created a class called `Account` that's interacting with the SQL tables and summarizing the data. To expand functionality of my app, I think managing multiple users with different IDs would be a good way to move forward. Furthermore, creating or establishing a logic that determines whether a transaction or payment is settled would make my app more appealing.

## Repo for front-end:
https://github.com/saulvegasauceda/pomelo-ts

### Note:
To run you might have to change the ports for the API endpoints and install node packages.
