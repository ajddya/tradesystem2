import streamlit as st

#シミュレーション結果を保存するクラス
class Simulation_Results:
    def __init__(self, dates, num, action_type, LEVEL, investment_result, buy_log, sell_log, Dividends, situational_bias, bias_class_port, pointed_out_bias, self_eval):
        self.dates = dates                             #実施日
        self.num = num                                 #実施回数
        self.action_type = action_type                 #行動型
        self.LEVEL = LEVEL                             #保有金額
        self.investment_result = investment_result     #投資結果（利益）
        self.buy_log = buy_log                         #購入ログ
        self.sell_log = sell_log                       #売却ログ
        self.Dividends = Dividends                     #配当に関するデータ
        self.situational_bias = situational_bias       #状況依存バイアス
        self.bias_class_port = bias_class_port         #バイアス分類レーダーチャート
        self.pointed_out_bias = pointed_out_bias       #指摘したバイアス
        self.self_eval = self_eval                     #事後自己評価
        self._observers = []

    def display(self):
        # ここに、このクラスのデータを表示するためのコードを追加できます
        st.write(f"実施日: {self.dates}")
        st.write(f"レベル：{self.LEVEL}")
        st.write(f"行動傾向: {self.action_type}")
        st.write(f"利益: {self.investment_result}") 

        check = st.checkbox("投資行動の情報を表示", value = False)
        if check:
            st.write("購入ログ:")
            st.write(self.buy_log)

            st.write("売却ログ:")
            st.write(self.sell_log)

            st.write("状況依存バイアス:")
            st.write(self.situational_bias)

            st.write("各バイアスのスコア:")
            st.write(self.pointed_out_bias)

            st.write("事後自己評価:")
            st.write(self.self_eval)

        st.write("")

        st.write("バイアスの各分類のスコア:")
        st.write(self.bias_class_port)

        # 平均点が高い順（降順）に並び替え
        bias_score_df_sorted = self.pointed_out_bias.sort_values(by="点数", ascending=False).reset_index(drop=True)


        st.write("指摘バイアス")
        for i in range(0,3):
            bias = bias_score_df_sorted["バイアス"][i]
            st.markdown(f'<p style="font-family:fantasy; color:blue; font-size: 24px;">・{bias}</p>', unsafe_allow_html=True)


