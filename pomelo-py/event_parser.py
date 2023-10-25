from account import Account

def summarize(inputJSON):
    manager = DataManager(inputJSON)
    return manager.summarize()

class DataManager:
    def __init__(self, credit_limit=1000):
        self.account = Account(credit_limit)
        self.function_dict = {
            "TXN_AUTHED": self.account.authorize_transaction,
            "TXN_SETTLED": self.account.settle_transaction,
            "TXN_AUTH_CLEARED": self.account.clear_transaction,
            "PAYMENT_INITIATED": self.account.initialize_payment,
            "PAYMENT_POSTED": self.account.post_payment,
            "PAYMENT_CANCELED": self.account.cancel_payment,
        }

    def _get_args(self, event):
        args = [
            event.get("eventType"),
            event.get("eventTime"),
            event.get("txnId"),
            event.get("amount"),
        ]

        # filter out no arguments
        return [a for a in args if a is not None]
    
    def parse_event(self, event):
        args = self._get_args(event)
        event_type = args[0]

        if event_type in self.function_dict:
            fxn = self.function_dict[event_type]
            fxn(*args[1:])
        else:
            raise ValueError(f"Command '{event_type}' not found in the dictionary.")
        
    def _parse_all_events(self, events):
        for event in events:
            self.parse_event(event)

        
    def summarize(self):
        pending_events = self.account.get_filtered_events(p_state="PAYMENT_INITIATED", txn_state="TXN_AUTHED")
        # get top 3 most recent settled event
        settled_events = self.account.get_filtered_events(p_state="PAYMENT_POSTED", txn_state="TXN_SETTLED", k=3)
        summary_data = {
            "availableCredit": self.account.available_credit,
            "payableBalance": self.account.payable_balance,
            "pendingEvents": pending_events,
            "settledEvents": settled_events,
        }

        return summary_data