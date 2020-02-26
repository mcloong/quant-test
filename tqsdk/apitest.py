from tqsdk import TqApi, TqAccount

api = TqApi()
serial = api.get_tick_serial("SHFE.rb2005")
position = api.get_position("SHFE.rb2005")
#print(position.float_profit_long + position.float_profit_short)
account = api.get_account()
print(account.float_profit, account.available, account.static_balance)
while True:
    api.wait_update()
   # print(serial);
   # print(serial.iloc[-1].bid_price1, serial.iloc[-1].ask_price1, serial.iloc[-1].average)
    print(position.exchange_id, position.pos_long , position.pos_long)