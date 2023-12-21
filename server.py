import tkinter as tk
import threading
from collections import defaultdict
from python_banyan.banyan_base import BanyanBase
import time

class EchoServer(BanyanBase):
    def __init__(self):
        super(EchoServer, self).__init__(process_name='Server')
        self.set_subscriber_topic('echo')
        self.time = 0
        self.bids = {}
        self.countdown_active = False

        self.main = tk.Tk()
        self.main.title("SERVER")
        self.main.resizable(False, False)


        self.main_textbox = tk.Text(self.main, width=40, height=30, state=tk.DISABLED, font=('Arial',10))
        self.main_textbox.grid(row=0, column=0, padx=10, pady=10, columnspan=4)

        self.main_label = tk.Label(self.main, text="Countdown (Seconds):")
        self.main_label.grid(row=1, column=0, padx=10, pady=10)

        self.main_entry = tk.Entry(self.main, width=10)
        self.main_entry.grid(row=1, column=1, padx=10, pady=10)

        self.main_button_start = tk.Button(self.main, text="Start", command=self.start_countdown, width=5)
        self.main_button_start.grid(row=1, column=2, pady=10)

        self.main_button_close = tk.Button(self.main, text="Close", command=self.close_countdown, width=5, state=tk.DISABLED)
        self.main_button_close.grid(row=1, column=3, padx=10, pady=10)
        
        threading.Thread(target=self.receive_loop).start()

        self.main.mainloop()
    def start_countdown(self):
        self.time = int(self.main_entry.get())
        self.main_entry.configure(state=tk.DISABLED)
        self.main_button_start.configure(state=tk.DISABLED)
        self.main_button_close.configure(state=tk.NORMAL)
        threading.Thread(target=self.countdown).start()

    def close_countdown(self):
        self.time = 1
        self.main_button_close.configure(state=tk.DISABLED)

    def countdown(self):
        while True:
            self.publish_payload({'time': self.time}, 'reply')
            if self.time == 0:
                self.main_entry.configure(state=tk.NORMAL)
                self.main_button_start.configure(state=tk.NORMAL)
                self.main_button_close.configure(state=tk.DISABLED)

                for item_name, bid_data in self.bids.items():
                    self.bid_list = bid_data['bids']
                    self.bidder_list = bid_data['bidders']

                    self.highest_bid_index = max(enumerate(self.bid_list), key=lambda x: x[1])[0]
                    self.highest_bid = self.bid_list[self.highest_bid_index]
                    self.highest_bidder_name = self.bidder_list[self.highest_bid_index]

                    self.item_name = item_name
                    self.publish_payload({'item_name':self.item_name, 'highest_bid':self.highest_bid, 'highest_bidder':self.highest_bidder_name}, 'reply')
                    self.main_textbox.configure(state=tk.NORMAL)
                    text = f"[{self.highest_bidder_name}] {self.item_name} => {self.highest_bid} \n"
                    self.main_textbox.insert(tk.END, f"WINNER!!! {text}")
                break
            
            time.sleep(1)
            self.time -= 1
             
    def incoming_message_processing(self, topic, payload):
        if 'client_name' in payload:
            self.main_textbox.configure(state=tk.NORMAL)
            self.main_textbox.insert(tk.END, f"{payload['client_name']} is ready...\n")
            self.main_textbox.configure(state=tk.DISABLED)

        if 'sell_item_name' in payload and 'sell_item_price' in payload and 'seller_name' in payload:
            self.main_textbox.configure(state=tk.NORMAL)
            self.main_textbox.insert(tk.END, f"Selling: {payload['sell_item_name']}, Php{payload['sell_item_price']} [{payload['seller_name']}]\n")
            self.main_textbox.configure(state=tk.DISABLED)
            self.publish_payload({'sell_item_name':payload['sell_item_name'], 'sell_item_price':payload['sell_item_price'], 'seller_name':payload['seller_name']}, 'reply')
            
        if 'bid_item_name' in payload and 'bid_price' in payload and 'bidder_name' in payload:
            self.main_textbox.configure(state=tk.NORMAL)
            self.main_textbox.insert(tk.END, f"Bidding: {payload['bid_item_name']}, Php{payload['bid_price']} [{payload['bidder_name']}]\n")
            self.main_textbox.configure(state=tk.DISABLED)
            self.publish_payload({'bid_item_name':payload['bid_item_name'],'bid_price':payload['bid_price'], 'bidder_name':payload['bidder_name']}, 'reply')
            if payload['bid_item_name'] not in self.bids:
                self.bids[payload['bid_item_name']] = {'bids':[payload['bid_price']], 'bidders':[payload['bidder_name']]}
                
            else:
                self.bids[payload['bid_item_name']]['bids'].append(payload['bid_price'])
                self.bids[payload['bid_item_name']]['bidders'].append(payload['bidder_name'])
                


def echo_server():
    EchoServer()

if __name__ == '__main__':
    echo_server()