import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
from PIL import Image

st.set_page_config(page_title="Cricket Pro Analytics", layout="wide")

# Load Data
@st.cache_data
def load_data():
    m = pd.read_csv('matches.csv')
    d = pd.read_csv('deliveries.csv')
    d['runs_total'] = d['runs_off_bat'] + d['extras'].fillna(0)
    return m, d

matches, deliveries = load_data()

# CSS for Transparent Premium Look
def set_bg():
    try:
        with open("cric_stadium.jpg", "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64}");
                background-size: cover;
                background-attachment: fixed;
            }}
            .glass {{
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255,255,255,0.1);
                color: white;
                margin-bottom: 25px;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                background-color: rgba(0,0,0,0.85);
                border-radius: 12px;
                padding: 10px;
                gap: 15px;
            }}
            .stTabs [data-baseweb="tab"] {{
                color: white !important;
                font-weight: bold;
                font-size: 16px;
            }}
            h1, h2, h3, h4, .stMetric label {{
                color: white !important;
                text-shadow: 2px 2px 4px #000;
            }}
            .stDataFrame, .stTable {{
                background: rgba(255, 255, 255, 0.05);
                color: white !important;
            }}
            </style>
        """, unsafe_allow_html=True)
    except: pass

set_bg()

# Header (Logo & Title)
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try: st.image(Image.open('logo.jpg'), width=150)
    except: pass
with col_title:
    st.markdown("<h1 style='font-size: 45px; margin-top: 10px;'>ICC T20 WORLD CUP 2024</h1>", unsafe_allow_html=True)

# Tabs Navigation
tabs = st.tabs(["🏆 OVERVIEW", "🎯 MATCH RESULTS", "📝 SCORECARDS", "👤 PLAYER STATS", "⚔️ TEAM H2H", "🚀 TEAM JOURNEY"])

teams = sorted(pd.unique(matches[['team1', 'team2']].values.ravel()))
bowl_wickets = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']

# --- TAB 1: OVERVIEW ---
with tabs[0]:
    winner = matches[matches['match_type'] == 'Final'].iloc[0]['winner'] if 'Final' in matches['match_type'].values else matches.iloc[-1]['winner']
    st.markdown(f"""
        <div class='glass' style='text-align:center; border: 3px solid #ffd700;'>
            <h1 style='color:#ffd700 !important; font-size: 50px; margin:0;'>🏆 CHAMPIONS: {winner.upper()} 🏆</h1>
            <h2 style='color:#ffd700 !important; margin-top:10px;'>🌟 PLAYER OF THE SERIES: JASPRIT BUMRAH 🌟</h2>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("TOURNAMENT RUNS", f"{int(deliveries['runs_total'].sum()):,}")
    c2.metric("TOURNAMENT WICKETS", int(deliveries['wicket_type'].count()))
    c3.metric("MOST MATCH AWARDS", matches['player_of_match'].mode()[0])

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("### 🔝 Top 5 Batsmen")
        st.table(deliveries.groupby(['striker', 'batting_team'])['runs_off_bat'].sum().reset_index().rename(columns={'striker':'Player','batting_team':'Team','runs_off_bat':'Runs'}).sort_values('Runs', ascending=False).head(5))
        
        st.markdown("### ⚡ Best Strike Rates (Min 100 Runs)")
        bat_runs = deliveries.groupby('striker')['runs_off_bat'].sum()
        balls = deliveries[deliveries['wides'].isna() | (deliveries['wides'] == 0)].groupby('striker').size()
        sr_stats = pd.DataFrame({'Runs': bat_runs, 'Balls': balls})
        sr_stats['Strike Rate'] = (sr_stats['Runs'] / sr_stats['Balls'] * 100).round(2)
        st.table(sr_stats[sr_stats['Runs'] >= 100].sort_values('Strike Rate', ascending=False).head(5)[['Strike Rate']])

    with g2:
        st.markdown("### 🥎 Top 5 Bowlers")
        st.table(deliveries[deliveries['wicket_type'].isin(bowl_wickets)].groupby(['bowler', 'bowling_team']).size().reset_index(name='Wickets').rename(columns={'bowler':'Player','bowling_team':'Team'}).sort_values('Wickets', ascending=False).head(5))
        
        st.markdown("### 🎯 Best Bowling Average (Min 5 Wkts)")
        runs_con = deliveries.groupby('bowler')['runs_total'].sum()
        wkts = deliveries[deliveries['wicket_type'].isin(bowl_wickets)].groupby('bowler').size()
        b_avg = pd.DataFrame({'Runs': runs_con, 'Wickets': wkts}).fillna(0)
        b_avg['Bowling Avg'] = (b_avg['Runs'] / b_avg['Wickets'].replace(0, np.nan)).round(2)
        st.table(b_avg[b_avg['Wickets'] >= 5].sort_values('Bowling Avg').head(5)[['Bowling Avg']])

    st.subheader("📊 Points Table")
    pt = [{'Team': t, 'Played': len(matches[(matches['team1'] == t) | (matches['team2'] == t)]), 'Win': len(matches[matches['winner'] == t]), 'Points': len(matches[matches['winner'] == t])*2} for t in teams]
    st.dataframe(pd.DataFrame(pt).sort_values('Points', ascending=False), use_container_width=True, hide_index=True)
#----TAB 2: Match Results----------
with tabs[1]:
    
    sel_team = st.selectbox("Select Team for Results", teams)
    t_matches = matches[(matches['team1'] == sel_team) | (matches['team2'] == sel_team)]
    for idx, row in t_matches.iterrows():
        st.write(f"**Match {row['match_number']}**: {row['team1']} vs {row['team2']} | Winner: **{row['winner']}** | MoM: **{row['player_of_match']}**")
        st.divider()
# --- TAB 3: SCORECARDS ---
with tabs[2]:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    sc_team = st.selectbox("Select Team", teams, key="score_team")
    m_opts = matches[(matches['team1'] == sc_team) | (matches['team2'] == sc_team)]
    m_pick = st.selectbox("Pick Match Scorecard", m_opts.apply(lambda x: f"Match {x['match_number']}: {x['team1']} vs {x['team2']}", axis=1))
    
    m_num = int(m_pick.split(":")[0].split(" ")[1])
    m_del = deliveries[deliveries['match_id'] == (m_num - 1)]
    
    for inn in [1, 2]:
        idata = m_del[m_del['innings'] == inn]
        if not idata.empty:
            bat_team = idata['batting_team'].iloc[0]
            total_r = idata['runs_total'].sum()
            total_w = idata['wicket_type'].count()
            legal_b = idata[(idata['wides']==0) & (idata['noballs']==0)].shape[0]
            overs = f"{legal_b // 6}.{legal_b % 6}"
            
            st.markdown(f"### {bat_team}: {int(total_r)}/{total_w}") #({overs} Overs)")
            
            # Batting
            bat = idata.groupby('striker').agg({'runs_off_bat':'sum', 'ball':'count'}).reset_index().rename(columns={'striker':'PLAYER NAME', 'runs_off_bat':'RUNS', 'ball':'BALLS'})
            bat['S/R'] = (bat['RUNS'] / bat['BALLS'] * 100).round(2)
            st.dataframe(bat, hide_index=True, use_container_width=True)
            # Bowling
            bowl = idata.groupby('bowler').agg({'runs_total':'sum', 'wicket_type':'count'}).reset_index().rename(columns={'bowler':'PLAYER NAME', 'runs_total':'CONCEDED', 'wicket_type':'WICKETS'})
            st.dataframe(bowl, hide_index=True, use_container_width=True)
            st.divider()
    st.markdown("</div>", unsafe_allow_html=True)

#---TAB 3----------
with tabs[3]:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    p_name = st.selectbox("Search Player", sorted(deliveries['striker'].unique()))
    p_d = deliveries[deliveries['striker'] == p_name]
    m_r = p_d.groupby('match_id')['runs_off_bat'].sum()
    
    # Calculate Correct Strike Rate
    p_runs = p_d['runs_off_bat'].sum()
    p_balls = p_d[p_d['wides'].isna() | (p_d['wides'] == 0)].shape[0]
    p_sr = (p_runs / p_balls * 100).round(2) if p_balls > 0 else 0
    
    # Boundary counts
    p_4s = len(p_d[p_d['runs_off_bat'] == 4])
    p_6s = len(p_d[p_d['runs_off_bat'] == 6])
    
    # Milestones
    fifties = len(m_r[(m_r >= 50) & (m_r < 100)])
    hundreds = len(m_r[m_r >= 100])
    
    # Wickets
    p_w = deliveries[(deliveries['bowler'] == p_name) & (deliveries['wicket_type'].isin(bowl_wickets))].shape[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Runs", int(p_runs))
    col2.metric("Strike Rate", p_sr)
    col3.metric("Total 4s", p_4s)
    col4.metric("Total 6s", p_6s)
    
    st.divider()
    
    col5, col6, col7 = st.columns(3)
    col5.metric("50s", fifties)
    col6.metric("100s", hundreds)
    col7.metric("Wickets Taken", p_w)
    st.markdown("</div>", unsafe_allow_html=True)
#----TAB 4-----
with tabs[4]:
    ta = st.selectbox("Team A", teams, index=0)
    tb = st.selectbox("Team B", teams, index=1)
    h2h = matches[((matches['team1'] == ta) & (matches['team2'] == tb)) | ((matches['team1'] == tb) & (matches['team2'] == ta))]
    if not h2h.empty: st.plotly_chart(px.pie(h2h, names='winner', title=f"Win Ratio: {ta} vs {tb}"))
    else: st.warning("No head-to-head matches found.")
# --- TAB 6: TEAM JOURNEY ---
with tabs[5]:
    jt = st.selectbox("Track Team Journey", teams)
    j_df = matches[(matches['team1'] == jt) | (matches['team2'] == jt)].copy()
    j_df['Result'] = j_df['winner'].apply(lambda x: "✅ WIN" if x == jt else "❌ LOSS")
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.table(j_df[['date', 'team1', 'team2', 'venue', 'Result']])
    st.markdown("</div>", unsafe_allow_html=True)