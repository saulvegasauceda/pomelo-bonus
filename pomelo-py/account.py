import sqlite3

class Account:
    def __init__(self, credit_limit):
        self.credit_balance = credit_limit

        self.available_credit = credit_limit
        self.payable_balance = 0
        # storing event history in db
        self.conn = sqlite3.connect('event_history.db', check_same_thread=False)
        self._db_create_tables()

    def _db_create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                init_time TIMESTAMP,
                finalized_time TIMESTAMP,
                event_type TEXT,
                txn_id TEXT,
                amount REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                init_time TIMESTAMP,
                finalized_time TIMESTAMP,
                event_type TEXT,
                txn_id TEXT,
                amount REAL
            )
        ''')

        self.conn.commit()

    def _db_add_event(self, table_name, event_type, time, txn_id, amount):
        cursor = self.conn.cursor()

        cursor.execute(f'SELECT COUNT(*) FROM {table_name} WHERE txn_id = ?', (txn_id,))
        count = cursor.fetchone()[0]

        if count == 0:
            # no existing entry with the same txn_id, so insert the new event
            cursor.execute(f'''
                INSERT INTO {table_name} (event_type, init_time, txn_id, amount)
                VALUES (?, ?, ?, ?)
            ''', (event_type, time, txn_id, amount))
            self.conn.commit()
        else:
            print(f'Event with txn_id {txn_id} already exists in the {table_name} table.')

    def _db_settle_transaction(self, txn_id, new_finalized_time, new_amount):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET finalized_time = ?,
                event_type = ?,
                amount = ?
            WHERE txn_id = ?
        ''', (new_finalized_time, "TXN_SETTLED", new_amount, txn_id))

        self.conn.commit()

    def _db_post_payment(self, txn_id, new_finalized_time):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE payments
            SET finalized_time = ?,
                event_type = ?
            WHERE txn_id = ?
        ''', (new_finalized_time, "PAYMENT_POSTED", txn_id))

        self.conn.commit()

    def _db_delete_event(self, table_name, txn_id):
        cursor = self.conn.cursor()
        cursor.execute(f'''
            DELETE FROM {table_name}
            WHERE txn_id = ?
        ''', (txn_id,))
        self.conn.commit()

    def _db_get_amount_by_txn_id(self, table_name, txn_id):
        cursor = self.conn.cursor()

        cursor.execute(f'''
            SELECT amount FROM {table_name}
            WHERE txn_id = ?
        ''', (txn_id,))

        result = cursor.fetchone()

        if result:
            return result[0] 
        else:
            return None
        
    def _db_get_filtered_events(self, p_state, txn_state, k=None):
        cursor = self.conn.cursor()

        cursor.execute(f'''
            SELECT init_time, finalized_time, event_type, txn_id, amount
            FROM (
                SELECT init_time, finalized_time, event_type, txn_id, amount
                FROM transactions
                WHERE event_type = "{txn_state}"
                UNION ALL
                SELECT init_time, finalized_time, event_type, txn_id, amount
                FROM payments
                WHERE event_type = "{p_state}"
            ) AS combined_entries
            ORDER BY init_time DESC
        ''')
        all_entries = cursor.fetchall()
        
        # return all entries if k is not specified or greater than the number of entries
        if k is None or k >= len(all_entries):
            return all_entries

        # return the top k entries if k is specified and within bounds
        return all_entries[:k]


        return top_k_entries

    def authorize_transaction(self, time, txn_id, amount):
        self._db_add_event("transactions","TXN_AUTHED", time, txn_id, amount)
        # decrease available credit
        self.available_credit -= amount

    def settle_transaction(self, time, txn_id, amount):
        prev_amount = self._db_get_amount_by_txn_id("transactions", txn_id)
        if prev_amount:
            # only charge new amount
            self.available_credit = (self.available_credit + prev_amount) - amount
            # add to payable balance
            self.payable_balance += amount
            self._db_settle_transaction(txn_id, time, amount)

    def clear_transaction(self, time, txn_id):
        prev_amount = self._db_get_amount_by_txn_id("transactions", txn_id)
        if prev_amount:
            # reset available credit
            self.available_credit += prev_amount

        self._db_delete_event("transactions", txn_id)


    def initialize_payment(self, time, p_id, amount):
        self._db_add_event("payments","PAYMENT_INITIATED", time, p_id, amount)
        # only reduce payable balance
        # amount is negative
        self.payable_balance += amount

    def post_payment(self, time, p_id):
        amount = self._db_get_amount_by_txn_id("payments", p_id)
        if amount:
            # free up credit
            # amount is negative
            self.available_credit -= amount
            # finalize payment
            self._db_post_payment(p_id, time)
            

    def cancel_payment(self, time, p_id):
        prev_amount = self._db_get_amount_by_txn_id("payments", p_id)
        if prev_amount:
            # reset payable balance
            self.payable_balance -= prev_amount

        self._db_delete_event("payments", p_id)

    def _unpack_event(self, event, table_id):
        init_time, finalized_time, event_type, txn_id, amount = event 
        return {
            "id": table_id,
            "txnID": txn_id,
            "amount": amount,
            "initTime": init_time,
            "finalizedTime": finalized_time,
        }
    
    def get_filtered_events(self, p_state, txn_state, k=None):
        raw_event_info = self._db_get_filtered_events(p_state, txn_state, k)

        return [
            self._unpack_event(event, i + 1) for i, event in enumerate(raw_event_info)
        ]