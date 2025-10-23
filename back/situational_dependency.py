import streamlit as st
import pandas as pd
import datetime as dt



# 各取引のアドバイス生成
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
        
    #現在志向バイアス　　売った後１ヶ月以内に最大値があるなら指摘
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
        situational_bias_df_temp['指摘バイアス'] = ['現在志向バイアス']
        situational_bias_df_temp['指摘銘柄数'] = [len(present_oriented_df)]
        situational_bias_df_temp['影響率'] = [len(present_oriented_df) / len(sell_log)]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

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

    
    #ブレークイーブン効果　　損失が出でいる株価に買い増しをしている
    BE_effect_df = pd.DataFrame()

    sell_log_temp_2 = sell_log.copy()
    # sell_log の '年月' 列を datetime 型に変換
    sell_log_temp_2['年月'] = pd.to_datetime(sell_log_temp_2['年月'], format="%Y/%m/%d")

        # 購入時、すでにその株を持っているか確認
        # buy_dfのうち、シミュレーション開始からnowまでの購入履歴を参照
    for i in range(1, len(buy_log)):
        buy_day = buy_log.iloc[i]['年月']
        buy_day = dt.datetime.strptime(buy_day, "%Y/%m/%d")
        buy_com_name = buy_log.iloc[i]['企業名']
        # 購入前の購入履歴を確認
        for j in range(0, i):
            buy_com_name_temp = buy_log.iloc[j]['企業名']
            # 購入銘柄と同じ銘柄があるか確認
            if buy_com_name == buy_com_name_temp:
                buy_day_temp = buy_log.iloc[j]['年月']
                buy_day_temp = dt.datetime.strptime(buy_day_temp, "%Y/%m/%d")

                # buy_day_temp ～ buy_day の範囲に含まれるデータを抽出
                mask = (sell_log_temp_2['年月'] >= buy_day_temp) & (sell_log_temp_2['年月'] <= buy_day)
                sell_period_df = sell_log.loc[mask].copy()
                # sell_log の中に buy_day_temp ~ buy_day 以内に売却されていないかを確認
                if buy_com_name in sell_period_df['企業名']:
                    break
                else:
                    # 保有株がマイナスかどうか確認する
                    # 過去購入時の株価取得
                    index2 = st.session_state.c_master.loc[(st.session_state.c_master['企業名']==buy_com_name_temp)].index.values[0]
                    buy_day_KK_temp = st.session_state.loaded_companies[index2].rdf_all[buy_day_temp : buy_day_temp]
                    # buy_dayの株価を取得
                    buy_day_KK_temp = buy_day_KK_temp['Close'].iloc[0]

                    # 新購入時の株価を取得
                    index = st.session_state.c_master.loc[(st.session_state.c_master['企業名']==buy_com_name)].index.values[0]
                    buy_day_KK = st.session_state.loaded_companies[index].rdf_all[buy_day : buy_day]
                    # buy_dayの株価を取得
                    buy_day_KK = buy_day_KK['Close'].iloc[0]

                    # 過去購入時の株価より新購入時の株価が低い場合影響を受けていると判定
                    if buy_day_KK_temp > buy_day_KK:
                        # 1つの行をDataFrameとして連結する
                        temp_df = pd.DataFrame(buy_log.iloc[i]).transpose()
                        BE_effect_df = pd.concat([BE_effect_df, temp_df], ignore_index=True)


    if BE_effect_df.empty == False:
        situational_bias_df_temp['企業名'] = [BE_effect_df.iloc[0]['企業名']]
        situational_bias_df_temp['指摘バイアス'] = ['ブレークイーブン効果']
        situational_bias_df_temp['指摘銘柄数'] = [len(BE_effect_df)]
        situational_bias_df_temp['影響率'] = [len(BE_effect_df) / len(sell_log)]
        situational_bias_df = pd.concat([situational_bias_df,situational_bias_df_temp], ignore_index=True)

    return situational_bias_df
