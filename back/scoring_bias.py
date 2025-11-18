import streamlit as st
import pandas as pd

# バイアスの影響度点数を計算する
def scoring_bias(personal_df, situational_bias_df, after_simulation_self_eval_df):
    bias_score_df = pd.DataFrame(columns=['バイアス', '点数'])
    bias_score_df_temp = pd.DataFrame(columns=['バイアス', '点数'])

    max_cognition_score = 5
    max_self_eval_score = 4

    # 損失回避傾向_______________________________________________________________________________________________________________
    # 外交性と負の相関
    character_score = (15 - personal_df["外交性"][0]) / 14
    
    # 認知課題Q5    max = 1
    cognition_score = personal_df["認知課題Q5"][0] / max_cognition_score
        
    # 事後自己評価Q1,△事後自己評価Q7,事後自己評価Q8     max = 1
    self_eval_score_1 = after_simulation_self_eval_df["事後自己評価Q1"][0] / max_self_eval_score
    self_eval_score_2 = (5 - after_simulation_self_eval_df["事後自己評価Q7"][0]) / max_self_eval_score
    self_eval_score_3 = after_simulation_self_eval_df["事後自己評価Q8"][0] / max_self_eval_score

        # 平均スコア算出
    self_eval_score = (self_eval_score_1 + self_eval_score_2 + self_eval_score_3) / 3
        
    # 損失銘柄ほど保有期間が長い,	購入金額比率が低く安定している,	主な購入根拠が「リスクが少ない」     max = 3
    situation_score_1 = 0
    if "損失回避傾向" in situational_bias_df["指摘バイアス"].tolist():
        situation_score_1 += 0.7

    if "損失回避傾向2" in situational_bias_df["指摘バイアス"].tolist():
        situation_score_1 += 0.7

    if after_simulation_self_eval_df["事後自己評価Q15"][0] == "リスクが少ない":
        situation_score_1 += 0.7

    # 重みをつけたスコア計算    性格：認知課題：事後事故評価：状況依存 ＝ 1.5 : 1.5 : 3 : 4
    score = (character_score * 0.15) + (cognition_score * 0.15) + (self_eval_score * 0.3) + (situation_score_1 * 0.4)
    if score > 1:
        score = 1

    bias_score_df_temp['バイアス'] = ['損失回避傾向']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 近視眼的思考_______________________________________________________________________________________________________________
    # 認知課題Q4	
    cognition_score = personal_df["認知課題Q4"][0] / max_cognition_score
   
    # 事後自己評価Q8	
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q8"][0] / max_self_eval_score
   
    # 売却時の過去1週間で5%以上の株価変動,	頻繁な取引
    situation_score = 0
    if "近視眼的思考" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    if "損失回避傾向2" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    # 重みをつけたスコア計算    認知課題：事後事故評価：状況依存 ＝ 2 : 3 : 5
    score =  (cognition_score * 0.2) + (self_eval_score * 0.3) + (situation_score * 0.5)
    if score > 1:
        score = 1

    bias_score_df_temp['バイアス'] = ['近視眼的思考']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # ブレークイーブン効果_______________________________________________________________________________________________________________
    # 認知課題Q14	
    cognition_score = personal_df["認知課題Q14"][0] / max_cognition_score

    # 事後自己評価Q1	△事後自己評価Q7	事後自己評価Q8		
    self_eval_score_1 = after_simulation_self_eval_df["事後自己評価Q1"][0] / max_self_eval_score
    self_eval_score_2 = (5 - after_simulation_self_eval_df["事後自己評価Q7"][0]) / max_self_eval_score
    self_eval_score_3 = after_simulation_self_eval_df["事後自己評価Q8"][0] / max_self_eval_score

        # 平均スコア算出
    self_eval_score = (self_eval_score_1 + self_eval_score_2 + self_eval_score_3) / 3
    
    # 保有中の損失銘柄に買い増し	株価損失時の購入金額比率が増加
    situation_score = 0
    if "ブレークイーブン効果" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    if "ブレークイーブン効果2" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    # 重みをつけたスコア計算    認知課題：事後事故評価：状況依存 ＝ 2 : 4 : 4
    score =  (cognition_score * 0.2) + (self_eval_score * 0.4) + (situation_score * 0.4)
    if score > 1:
        score = 1

    bias_score_df_temp['バイアス'] = ['ブレークイーブン効果']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 現在思考バイアス_______________________________________________________________________________________________________________
    # 認知課題Q4	
    cognition_score = personal_df["認知課題Q4"][0] / max_cognition_score

    # 事後事故評価Q3				
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q3"][0] / max_self_eval_score

    # 売却後14日の間に最大株価が存在	平均保有期間が短い	主な売却根拠が「利益確定売り」
    situation_score = 0
    if "現在思考バイアス" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 0.5

    if "現在思考バイアス2" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    if after_simulation_self_eval_df["事後自己評価Q15"][0] == "確実な利益を得る":
        situation_score += 0.5

    # 重みをつけたスコア計算    認知課題：事後事故評価：状況依存 ＝ 2 : 4 : 4
    score =  (cognition_score * 0.2) + (self_eval_score * 0.4) + (situation_score * 0.4)
    if score > 1:
        score = 1

    bias_score_df_temp['バイアス'] = ['現在思考バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 現状維持バイアス_______________________________________________________________________________________________________________
    # 外交性・開放性と負の相関
    character_score_1 = (15 - personal_df["外交性"][0]) / 14
    character_score_2 = (15 - personal_df["開放性"][0]) / 14

    character_score = (character_score_1 + character_score_2) / 2

    # 認知課題Q6	△認知課題Q10			
    cognition_score_1 = personal_df["認知課題Q14"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q14"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2

    # 事後事故評価Q13
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q13"][0] / max_self_eval_score

    # 重みをつけたスコア計算    性格：認知課題：事後事故評価 ＝ 4 : 2 : 4
    score =  (character_score * 0.4) + (cognition_score * 0.2) + (self_eval_score * 0.4)

    bias_score_df_temp['バイアス'] = ['現状維持バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 楽観性バイアス_______________________________________________________________________________________________________________
    # 外交性・開放性と正の相関	神経症傾向と負の相関
    character_score_1 = personal_df["外交性"][0] / 14
    character_score_2 = personal_df["開放性"][0] / 14
    character_score_3 = (15 - personal_df["神経症傾向"][0]) / 14

    character_score = (character_score_1 + character_score_2 + character_score_3) / 3

    # 認知課題Q1	△認知課題Q7	
    cognition_score_1 = personal_df["認知課題Q1"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q7"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 事後自己評価Q5		
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q5"][0] / max_self_eval_score

    # 重みをつけたスコア計算    性格：認知課題：事後事故評価 ＝ 4 : 2 : 4
    score =  (character_score * 0.4) + (cognition_score * 0.2) + (self_eval_score * 0.4)

    bias_score_df_temp['バイアス'] = ['楽観性バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 自信過剰_______________________________________________________________________________________________________________
    # 認知課題2	△認知課題8	
    cognition_score_1 = personal_df["認知課題Q2"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q8"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 事後自己評価4	事後自己評価5
    self_eval_score_1 = after_simulation_self_eval_df["事後自己評価Q4"][0] / max_self_eval_score
    self_eval_score_2 = after_simulation_self_eval_df["事後自己評価Q5"][0] / max_self_eval_score

        # 平均スコア算出
    self_eval_score = (self_eval_score_1 + self_eval_score_2) / 2

    # 重みをつけたスコア計算    認知課題：事後事故評価 ＝ 5 : 5 
    score =  (cognition_score * 0.5) + (self_eval_score * 0.5)

    bias_score_df_temp['バイアス'] = ['自信過剰']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 保守主義バイアス_______________________________________________________________________________________________________________
    # 認知課題11	△認知課題17
    cognition_score_1 = personal_df["認知課題Q11"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q17"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 重みをつけたスコア計算    認知課題 ＝ 5
    score =  (cognition_score * 0.5)

    bias_score_df_temp['バイアス'] = ['保守主義バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 後知恵バイアス_______________________________________________________________________________________________________________
    # 認知課題15	△認知課題20	
    cognition_score_1 = personal_df["認知課題Q15"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q20"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 事後自己評価9
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q9"][0] / max_self_eval_score
    
    # 重みをつけたスコア計算    認知課題：事後事故評価 ＝ 4 : 6
    score =  (cognition_score * 0.4) + (self_eval_score * 0.6)

    bias_score_df_temp['バイアス'] = ['後知恵バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 自己正当化バイアス_______________________________________________________________________________________________________________
    # 認知課題16	△認知課題21	
    cognition_score_1 = personal_df["認知課題Q16"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q21"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 事後事故評価6 △事後自己評価11
    self_eval_score_1 = after_simulation_self_eval_df["事後自己評価Q6"][0] / max_self_eval_score
    self_eval_score_2 = (5 - after_simulation_self_eval_df["事後自己評価Q11"][0]) / max_self_eval_score

        # 平均スコア算出
    self_eval_score = (self_eval_score_1 + self_eval_score_2) / 2
    
    # 重みをつけたスコア計算    事後事故評価 ＝ 5 : 5
    score = (cognition_score * 0.5) + (self_eval_score * 0.5)

    bias_score_df_temp['バイアス'] = ['自己正当化バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # ハロー効果_______________________________________________________________________________________________________________
    # 認知課題13	△認知課題19	
    cognition_score_1 = personal_df["認知課題Q13"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q19"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 事後事故評価10
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q10"][0] / max_self_eval_score

    # 重みをつけたスコア計算    認知課題：事後事故評価 ＝ 5 : 5
    score =  (cognition_score * 0.5) + (self_eval_score * 0.5)

    bias_score_df_temp['バイアス'] = ['ハロー効果']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 権威バイアス_______________________________________________________________________________________________________________
    # 認知課題12	△認知課題18	
    cognition_score_1 = personal_df["認知課題Q12"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q18"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2
    
    # 事後事故評価2	
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q2"][0] / max_self_eval_score

    # 購入銘柄の専門家予想      主な売却根拠が「専門家予想」
    situation_score = 0
    if "権威バイアス" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    if after_simulation_self_eval_df["事後自己評価Q15"][0] == "専門家予想":
        situation_score += 1

    # 重みをつけたスコア計算    認知課題：事後事故評価：状況依存 ＝ 2 : 4 : 4
    score =  (cognition_score * 0.2) + (self_eval_score * 0.4) + (situation_score * 0.4)
    if score > 1:
        score = 1

    bias_score_df_temp['バイアス'] = ['権威バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)

    # 同調バイアス_______________________________________________________________________________________________________________
    # 認知課題3	△認知課題9	
    cognition_score_1 = personal_df["認知課題Q3"][0] / max_cognition_score
    cognition_score_2 = ((max_cognition_score + 1) - personal_df["認知課題Q9"][0]) / max_cognition_score

    cognition_score = (cognition_score_1 + cognition_score_2) / 2

    # 事後事故評価2	
    self_eval_score = after_simulation_self_eval_df["事後自己評価Q2"][0] / max_self_eval_score
    
    # 主な売却根拠が「みんなの予想」
    situation_score = 0
    if "同調バイアス" in situational_bias_df["指摘バイアス"].tolist():
        situation_score += 1

    if after_simulation_self_eval_df["事後自己評価Q15"][0] == "みんなが購入しているから":
        situation_score += 1

    # 重みをつけたスコア計算    認知課題：事後事故評価：状況依存 ＝ 2 : 4 : 4
    score =  (cognition_score * 0.2) + (self_eval_score * 0.4) + (situation_score * 0.4)
    if score > 1:
        score = 1

    bias_score_df_temp['バイアス'] = ['同調バイアス']
    bias_score_df_temp['点数'] = [round(score * 100, 1)]
    bias_score_df = pd.concat([bias_score_df,bias_score_df_temp], ignore_index=True)
    

    return bias_score_df
