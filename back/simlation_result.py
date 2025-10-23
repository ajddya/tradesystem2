import streamlit as st

#シミュレーション結果を保存するクラス
class Simulation_Results:
    def __init__(self, dates, num, action_type, LEVEL, investment_result, buy_log, sell_log, Dividends, bias_class_port, pointed_out_bias, self_eval):
        self.dates = dates                             #実施日
        self.num = num                                 #実施回数
        self.action_type = action_type                 #行動型
        self.LEVEL = LEVEL                             #保有金額
        self.investment_result = investment_result     #投資結果（利益）
        self.buy_log = buy_log                         #購入ログ
        self.sell_log = sell_log                       #売却ログ
        self.Dividends = Dividends                     #配当に関するデータ
        self.bias_class_port = bias_class_port         #バイアス分類ポートフォリオ
        self.pointed_out_bias = pointed_out_bias       #指摘したバイアス
        self.self_eval = self_eval                     #事後自己評価
        self._observers = []

    def display(self):
        # ここに、このクラスのデータを表示するためのコードを追加できます
        st.write(f"実施日: {self.dates}")
        st.write(f"レベル：{self.LEVEL}")
        st.write(f"分類型: {self.action_type}")
        st.write(f"利益: {self.investment_result}") 

        st.write("購入ログ:")
        st.write(self.buy_log)

        st.write("売却ログ:")
        st.write(self.sell_log)

        st.write("全体のアドバイス:")
        st.write(self.bias_class_port)

        st.write("各取引のアドバイス:")
        st.write(self.pointed_out_bias)

        st.write("事後自己評価:")
        st.write(self.self_eval)