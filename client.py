import argparse
import signal
import threading
import tkinter as tk
from python_banyan.banyan_base import BanyanBase
from tkinter import messagebox


class EchoCmdClient(BanyanBase):
    
    def __init__(self, **kwargs):
        super(EchoCmdClient, self).__init__(back_plane_ip_address=kwargs['back_plane_ip_address'],
                                            subscriber_port=kwargs['subscriber_port'],
                                            publisher_port=kwargs['publisher_port'],
                                            process_name=kwargs['process_name'],
                                            loop_time=kwargs['loop_time'])

        self.set_subscriber_topic('reply')
        
        self.client_name = ""
        def enter_name():
            self.client_name = self.main_entry.get()
            if self.client_name != '':
                self.publish_payload({'client_name':self.client_name}, 'echo')
                self.main.destroy()
                self.client_window()
            else:
                messagebox.showerror("Error!", "Invalid Name!")

        self.main = tk.Tk()
        self.main.title("ENTER YOUR NAME")
        self.main.resizable(False, False)

        self.main_entry = tk.Entry(self.main, width=20)
        self.main_entry.grid(row=0, column=0, padx=10, pady=10)

        self.main_button = tk.Button(self.main, text="Accept", command=enter_name, width=5)
        self.main_button.grid(row=0, column=1, padx=10, pady=10)

        threading.Thread(target=self.receive_loop).start()

        self.main.mainloop()
        
    def client_window(self):
        self.client = tk.Tk()
        self.client.title(f"CLIENT {self.client_name}")
        self.client.resizable(False, False)

        self.client_bid_items = []
        
        self.client_button_bid = tk.Button(self.client, text="Bid", command=self.bid_window, width=7, state=tk.DISABLED)
        self.client_button_bid.grid(row=0, column=0, padx=10, pady=10)

        self.client_button_sell = tk.Button(self.client, text="Sell", command=self.sell_window, width=7, state=tk.DISABLED)
        self.client_button_sell.grid(row=0, column=1, padx=5, pady=10)

        self.client_label_time = tk.Label(self.client, text="Time Left:")
        self.client_label_time.grid(row=0, column=2, padx=5, pady=10)

        self.client_text_time = tk.Text(self.client, width=5, height=1, state=tk.DISABLED)
        self.client_text_time.grid(row=0, column=3, padx=10, pady=10)
        
        self.client_label_bidding = tk.Label(self.client, text="Item for BIDDING:")
        self.client_label_bidding.grid(row=1, columnspan=4)        
        
        self.client_listbox_bidding = tk.Listbox(self.client, width=40, height=7)
        self.client_listbox_bidding.grid(row=2, columnspan=4, padx=10, pady=10)
        
        self.client_label_selling = tk.Label(self.client, text="Item you are SELLING:")
        self.client_label_selling.grid(row=3, columnspan=4)

        self.client_listbox_selling = tk.Listbox(self.client, width=40, height=7)
        self.client_listbox_selling.grid(row=4, columnspan=4, padx=10, pady=10)

        self.client_label_highest = tk.Label(self.client, text="BIDDERS:")
        self.client_label_highest.grid(row=5, columnspan=4)
        
        self.client_textbox_bidders = tk.Text(self.client, width=35, height=7, state=tk.DISABLED, font=('Arial',10))
        self.client_textbox_bidders.grid(row=6, columnspan=4, padx=10, pady=10)

        self.client.mainloop()
    def bid_window(self):
        self.bid = tk.Tk()
        self.bid.title("BIDDING...")
        self.bid.resizable(False, False)

        self.bidder_name = self.client_name
        self.bid_item_index = self.client_listbox_bidding.curselection()[0]
        self.bid_item_name = self.client_bid_items[self.bid_item_index][0]
        self.bid_item_price = self.client_bid_items[self.bid_item_index][1]
        self.bid_price = 0

        def accept_bid():
            self.bid_price = int(self.bid_entry_price.get())
            if self.bid_item_price < self.bid_price:
                self.publish_payload({'bid_item_name':self.bid_item_name, 'bid_price':self.bid_price, 'bidder_name':self.bidder_name}, 'echo')
                self.bid.destroy()
            
            else:
                messagebox.showerror('Error!','Bid price should be higher than the item price!')

        self.bid_label_item = tk.Label(self.bid, text=f"{self.bid_item_name}:")
        self.bid_label_item.grid(row=0, column=0, padx=10, pady=10)

        self.bid_entry_price = tk.Entry(self.bid, width=15)
        self.bid_entry_price.grid(row=0, column=1, pady=10)

        self.bid_button_accept = tk.Button(self.bid, text='Accept', command=accept_bid, width=5)
        self.bid_button_accept.grid(row=0, column=2, padx=10, pady=10)

        self.bid.mainloop()
        
    def sell_window(self):
        self.sell = tk.Tk()
        self.sell.title("SELLING...") 
        self.sell.resizable(False, False)

        self.seller_name = self.client_name
        self.sell_item_name = ''
        self.sell_item_price = 0

        def accept_sell():
            self.sell_item_name = self.sell_entry_item.get()
            self.sell_item_price = int(self.sell_entry_price.get())
            
            self.client_listbox_selling.insert(tk.END, f"{self.sell_item_name} Php{self.sell_item_price}")

            self.publish_payload({'sell_item_name':self.sell_item_name, 'sell_item_price':self.sell_item_price, 'seller_name':self.seller_name}, 'echo')

            self.sell.destroy()

        self.sell_label_item = tk.Label(self.sell, text='Item:')
        self.sell_label_item.grid(row=0, column=0, padx=10, pady=10)

        self.sell_entry_item = tk.Entry(self.sell, width=10)
        self.sell_entry_item.grid(row=0, column=1)

        self.sell_label_price = tk.Label(self.sell, text='Price:')
        self.sell_label_price.grid(row=0, column=2, padx=10, pady=10)

        self.sell_entry_price = tk.Entry(self.sell, width=10)
        self.sell_entry_price.grid(row=0, column=3)

        self.sell_button_accept = tk.Button(self.sell, text='Accept', command=accept_sell, width=5)
        self.sell_button_accept.grid(row=0, column=4, padx=10, pady=10)

        self.sell.mainloop()

    def incoming_message_processing(self, topic, payload):
        if 'time' in payload:
            self.client_text_time.configure(state=tk.NORMAL)
            self.client_text_time.delete('1.0', tk.END)
            self.client_text_time.insert(tk.END, payload['time'])
            self.client_text_time.configure(state=tk.DISABLED)
            self.client_button_bid.configure(state=tk.NORMAL)
            self.client_button_sell.configure(state=tk.NORMAL)
            if payload['time'] == 0:
                self.client_button_bid.configure(state=tk.DISABLED)
                self.client_button_sell.configure(state=tk.DISABLED)
                self.client_textbox_bidders.configure(state=tk.NORMAL)
                self.client_textbox_bidders.insert(tk.END, f"\n***********WINNERS************\n")
                self.client_textbox_bidders.configure(state=tk.DISABLED)

        if 'sell_item_name' in payload and 'sell_item_price' in payload and 'seller_name' in payload:
            if payload['seller_name'] != self.client_name:
                self.client_listbox_bidding.insert(tk.END, f"{payload['sell_item_name']}, Php{payload['sell_item_price']} [{payload['seller_name']}]")
                self.client_bid_items.append([payload['sell_item_name'], payload['sell_item_price']])

        if 'bid_item_name' in payload and 'bid_price' in payload and 'bidder_name' in payload:
            self.client_textbox_bidders.configure(state=tk.NORMAL)
            self.client_textbox_bidders.insert(tk.END, f"{payload['bid_item_name']} => {payload['bid_price']} [{payload['bidder_name']}]\n")
            self.client_textbox_bidders.configure(state=tk.DISABLED)

        if 'item_name' in payload and 'highest_bid' in payload and 'highest_bidder' in payload:
            self.client_textbox_bidders.configure(state=tk.NORMAL)
            self.client_textbox_bidders.insert(tk.END, f"WINNER!!! [{payload['highest_bidder']}] {payload['item_name']} => {payload['highest_bid']}\n")
            self.client_textbox_bidders.configure(state=tk.DISABLED)

def echo_cmdline_client():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-m", dest="number_of_messages", default="10",
                        help="Number of messages to publish")
    parser.add_argument("-n", dest="process_name", default="EchoCmdClient",
                        help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-t", dest="loop_time", default=".1",
                        help="Event Loop Timer in seconds")

    args = parser.parse_args()

    if args.back_plane_ip_address == 'None':
        args.back_plane_ip_address = None
    kw_options = {'back_plane_ip_address': args.back_plane_ip_address,
                  'number_of_messages': int(args.number_of_messages),
                  'publisher_port': args.publisher_port,
                  'subscriber_port': args.subscriber_port,
                  'process_name': args.process_name,
                  'loop_time': float(args.loop_time)}
    EchoCmdClient(**kw_options)

def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    echo_cmdline_client()
