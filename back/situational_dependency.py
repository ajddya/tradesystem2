import streamlit as st
import pandas as pd
import datetime as dt



# 売買履歴から状況依存バイアスの影響判定をする
def situational_dependency(buy_log, sell_log):
    situational_bias_df = pd.DataFrame(columns=['企業名', '指摘バイアス', '指摘銘柄数', '影響率'])
    situational_bias_df_temp = pd.DataFrame(columns=['企業名', '指摘バイアス', '指摘銘柄数', '影響率'])
    
    #損失回避性　　購入日の株価より小さな株価が売却びまで連続で続いている（損切りできていない）場合に指摘
    minas_benef_df = sell_log[sell_log['利益'] < 0]
    minas_benef_df = minas_benef_df.reset_index(drop=True)

    minas_seqence_df = pd.DataFrame()
    for i in range(0,len(minas_benef_df)):
        mbd_sell_day = minas_benef_df.iloc[i]['年月']
        mbd_sell_day = dt.datetime.strptime(mbd_sell_day, "%Y/%m/%d")
        mbd_com_name = minas_benef_df.iloc[i]['企業名']
        mbd_buy_day = buy_log[buy_log['企業名']==mbd_com_name]['年月'].iloc[-1]
        mbd_buy_day = dt.datetime.strptime(mbd_buy_day, "%Y/%m/%d")

        index = st.session_state.c_master.loc[(st.session_state.c_master['企業名']==mbd_com_name)].index.values[0]
        in_trade_rdf = st.session_state.loaded_companies[index].rdf_all[mbd_buy_day : mbd_sell_day]

        buy_day_KK = in_trade_rdf['Close'].iloc[0]

        # インデックスを日付型としてリセット
        in_trade_rdf = in_trade_rdf.reset_index()

        # Closeのカラムでbuy_day_KKよりも小さい値の場所をTrue、それ以外をFalseとする新しいカラムを作成
        in_trade_rdf['Below_Buy_Day_KK'] = in_trade_rdf['Close'] < buy_day_KK

        # 連続したTrueの数をカウントするための関数
        def count_true_consecutive(s):
            count = max_count = 0
            for v in s:
                if v:
                    count += 1
                    max_count = max(max_count, count)
                else:
                    count = 0
            return max_count

        # 連続してbuy_day_KKよりも小さい値が７日以上続く場所を見つける
        if count_true_consecutive(in_trade_rdf['Below_Buy_Day_KK']) >= 7:
            minas_seqence_df_temp = pd.DataFrame(minas_benef_df.iloc[i]).transpose()
            minas_seqence_df = pd.concat([minas_seqence_df, minas_seqence_df_temp], ignore_index = True)

    if minas_seqence_df.empty == False:
        situational_bias_df_temp['企業名'] = [minas_seqence_df.iloc[0]['企業名']]
        situational_bias_df_temp['指摘バイアス'] = ['損失回避傾向']
        situational_bias_df_temp['指摘銘柄数'] = [len(minas_seqence_df)]
        situational_bias_df_temp['影響率'] = [len(minas_seqence_df) / len(sell_log)]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    # 損失回避傾向２　　購入金額比率が低く安定している    
    low_buy_rate_df = buy_log[buy_log["購入金額比率"] <= 0.3].copy()

      # 全購入履歴のうち購入金額比率が低いものが75%以上なら影響ありと判定
    if len(low_buy_rate_df) / len(buy_log) >= 0.75:
        situational_bias_df_temp['企業名'] = ["指定なし"]
        situational_bias_df_temp['指摘バイアス'] = ['損失回避傾向2']
        situational_bias_df_temp['指摘銘柄数'] = ["指定なし"]
        situational_bias_df_temp['影響率'] = ["指定なし"]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

        
    #現在志向バイアス　　売った後１ヶ月以内に一株あたり得た利益以上の株価上昇があるなら指摘
    pluss_benef_df = sell_log[sell_log['利益'] > 0]
    pluss_benef_df = pluss_benef_df.reset_index(drop=True)

    present_oriented_df = pd.DataFrame()
    for i in range(0, len(pluss_benef_df)):
        pbd_sell_day = pluss_benef_df.iloc[i]['年月']
        pbd_sell_day = dt.datetime.strptime(pbd_sell_day, "%Y/%m/%d")
        end_date = pbd_sell_day + dt.timedelta(days=30)
        pbd_com_name = pluss_benef_df.iloc[i]['企業名']
        index = st.session_state.c_master.loc[(st.session_state.c_master['企業名']==pbd_com_name)].index.values[0]
        after_sell_day_KK = st.session_state.loaded_companies[index].rdf_all[pbd_sell_day : end_date]

        # sell_dayの株価を取得
        sell_day_KK = after_sell_day_KK['Close'].iloc[0]

        # sell_day後の最大closeの値を取得
        max_close_KK = after_sell_day_KK[after_sell_day_KK['Close']==after_sell_day_KK['Close'].max()]['Close'].iloc[0]

        if sell_day_KK < max_close_KK:
            if (max_close_KK - sell_day_KK) > (pluss_benef_df.iloc[i]['利益']/pluss_benef_df.iloc[i]['売却株式数']):
            # 1つの行をDataFrameとして連結する
                temp_df = pd.DataFrame(pluss_benef_df.iloc[i]).transpose()
                present_oriented_df = pd.concat([present_oriented_df, temp_df], ignore_index=True)
        
    if present_oriented_df.empty == False:
        situational_bias_df_temp['企業名'] = [present_oriented_df.iloc[0]['企業名']]
        situational_bias_df_temp['指摘バイアス'] = ['現在思考バイアス']
        situational_bias_df_temp['指摘銘柄数'] = [len(present_oriented_df)]
        situational_bias_df_temp['影響率'] = [len(present_oriented_df) / len(sell_log)]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    # 現在思考バイアス　　平均保有期間が短い
    #######################################################################################################
    buy_log_temp = buy_log.copy()
    buy_log_temp['年月'] = pd.to_datetime(buy_log_temp['年月'], format="%Y/%m/%d")
    trade_time_list = []

    for i in range(0,len(sell_log)):
        sell_day = sell_log.iloc[i]['年月']
        sell_day = dt.datetime.strptime(sell_day, "%Y/%m/%d")
        sell_com_name = sell_log.iloc[i]['企業名']
        # 売却日以前の購入履歴のうち、同じ企業のデータを抽出
        buy_log_temp_temp = buy_log_temp[(buy_log_temp["年月"] <= sell_day) & (buy_log_temp["企業名"] == sell_com_name)]
        # 対象データが存在する場合のみ処理
        if not buy_log_temp_temp.empty:
            # 最も直近の購入日（最大の年月）
            buy_day = buy_log_temp_temp["年月"].max()
            # 売却日 - 購入日 の差（日数）を計算
            delta_trade_time = (sell_day - buy_day).days  # → int（日数）に変換
            trade_time_list.append(delta_trade_time)

    # --- 平均保有期間を計算 ---
    if len(trade_time_list) > 0:
        trade_time_list_ave = sum(trade_time_list) / len(trade_time_list)
    else:
        trade_time_list_ave = None

    # 平均保有期間が7日以下なら影響ありと判定
    if trade_time_list_ave <= 7:
        situational_bias_df_temp['企業名'] = ["指定なし"]
        situational_bias_df_temp['指摘バイアス'] = ['現在思考バイアス2']
        situational_bias_df_temp['指摘銘柄数'] = ["指定なし"]
        situational_bias_df_temp['影響率'] = ["指定なし"]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    #######################################################################################################


    # 近視眼的思考　　売却する１週間以内に大きな株価変動があった
    foresight_df = pd.DataFrame()

        # sell_dfのうち、売却から１週間分の株価を取得
    for i in range(0, len(sell_log)):
        fore_sell_day = sell_log.iloc[i]['年月']
        fore_sell_day = dt.datetime.strptime(fore_sell_day, "%Y/%m/%d")
        pre_date_2 = fore_sell_day - dt.timedelta(days=7)
        fore_com_name = sell_log.iloc[i]['企業名']
        index = st.session_state.c_master.loc[(st.session_state.c_master['企業名']==fore_com_name)].index.values[0]
        pre_sell_day_KK = st.session_state.loaded_companies[index].rdf_all[pre_date_2 : fore_sell_day]

        # sell_dayの株価を取得
        sell_day_KK = pre_sell_day_KK['Close'].iloc[-1]

        # 指定期間中の最大closeの値を取得
        max_close_KK = pre_sell_day_KK[pre_sell_day_KK['Close']==pre_sell_day_KK['Close'].max()]['Close'].iloc[0]
        min_close_KK = pre_sell_day_KK[pre_sell_day_KK['Close']==pre_sell_day_KK['Close'].min()]['Close'].iloc[0]

        delta_close_KK = max_close_KK - min_close_KK

        # もし、１週間のうち売却時の株価の５％以上の変化があれば影響を受けていると判定
        if (sell_day_KK * 0.05) < delta_close_KK:
            # 1つの行をDataFrameとして連結する
            temp_df = pd.DataFrame(sell_log.iloc[i]).transpose()
            foresight_df = pd.concat([foresight_df, temp_df], ignore_index=True)


    if foresight_df.empty == False:
        situational_bias_df_temp['企業名'] = [foresight_df.iloc[0]['企業名']]
        situational_bias_df_temp['指摘バイアス'] = ['近視眼的思考']
        situational_bias_df_temp['指摘銘柄数'] = [len(foresight_df)]
        situational_bias_df_temp['影響率'] = [len(foresight_df) / len(sell_log)]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    # 近視眼的思考２　　頻繁な取引
    number_of_trade_limit = 10
    if len(sell_log) > number_of_trade_limit:
        situational_bias_df_temp['企業名'] = ["指定なし"]
        situational_bias_df_temp['指摘バイアス'] = ['近視眼的思考2']
        situational_bias_df_temp['指摘銘柄数'] = ["指定なし"]
        situational_bias_df_temp['影響率'] = ["指定なし"]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)
    
    #ブレークイーブン効果　　損失が出でいる株価に買い増しをしている
    BE_effect_df = pd.DataFrame()

    for i in range(0,len(buy_log)):
        if buy_log.iloc[i]["購入根拠"] == "ナンピン買い":
            temp_df = pd.DataFrame(buy_log.iloc[i]).transpose()
            BE_effect_df = pd.concat([BE_effect_df, temp_df], ignore_index=True)


    if BE_effect_df.empty == False:
        situational_bias_df_temp['企業名'] = [BE_effect_df.iloc[0]['企業名']]
        situational_bias_df_temp['指摘バイアス'] = ['ブレークイーブン効果']
        situational_bias_df_temp['指摘銘柄数'] = [len(BE_effect_df)]
        situational_bias_df_temp['影響率'] = [len(BE_effect_df) / len(buy_log)]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    #ブレークイーブン効果２　　株価損失時の購入金額比率が増加
        # 「購入根拠」が「ナンピン買い」または「含み損中買い」の行を抽出
    loss_buy_mask = buy_log["購入根拠"].isin(["ナンピン買い", "含み損中買い"])

        # 含み損中買い時（ナンピン買い含む）の平均購入金額比率
    loss_buy_ratio = buy_log.loc[loss_buy_mask, "購入金額比率"].mean()

        # 通常時（それ以外）の平均購入金額比率
    normal_buy_ratio = buy_log.loc[~loss_buy_mask, "購入金額比率"].mean()   

    if  loss_buy_ratio > normal_buy_ratio:
        situational_bias_df_temp['企業名'] = ["指定なし"]
        situational_bias_df_temp['指摘バイアス'] = ['ブレークイーブン効果2']
        situational_bias_df_temp['指摘銘柄数'] = ["指定なし"]
        situational_bias_df_temp['影響率'] = ["指定なし"]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    # 権威バイアス
    specialist_ave = buy_log["専門家予想"].mean()

    if specialist_ave <= 4:
        situational_bias_df_temp['企業名'] = ["指定なし"]
        situational_bias_df_temp['指摘バイアス'] = ['権威バイアス']
        situational_bias_df_temp['指摘銘柄数'] = ["指定なし"]
        situational_bias_df_temp['影響率'] = ["指定なし"]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    # 同調バイアス
    everyone_ave = buy_log["みんなの予想"].mean()

    if everyone_ave <= 4:
        situational_bias_df_temp['企業名'] = ["指定なし"]
        situational_bias_df_temp['指摘バイアス'] = ['同調バイアス']
        situational_bias_df_temp['指摘銘柄数'] = ["指定なし"]
        situational_bias_df_temp['影響率'] = ["指定なし"]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    return situational_bias_df
