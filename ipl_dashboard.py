import streamlit as st
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(page_title="IPL Team Scorer", layout="wide", initial_sidebar_state="expanded")

# Define file paths
BASE_DIR = Path(__file__).parent
BATTERS_CSV = BASE_DIR / "IPL_Auction_2026 - Batters.csv"
BOWLERS_CSV = BASE_DIR / "IPL_Auction_2026 - Bowlers.csv"
ALLROUNDERS_CSV = BASE_DIR / "IPL_Auction_2026 - All-rounders.csv"
TEAMS_JSON = BASE_DIR / "teams_data.json"

# ==================== UTILITY FUNCTIONS ====================

def load_player_data():
    """Load all player data from CSV files"""
    batters = pd.read_csv(BATTERS_CSV)
    bowlers = pd.read_csv(BOWLERS_CSV)
    allrounders = pd.read_csv(ALLROUNDERS_CSV)
    
    # Add player type
    batters['Type'] = 'Batter'
    bowlers['Type'] = 'Bowler'
    allrounders['Type'] = 'All-rounder'
    
    return batters, bowlers, allrounders

def get_all_players_list(batters, bowlers, allrounders):
    """Get a combined list of all players with their types"""
    players = []
    
    for idx, row in batters.iterrows():
        players.append({'Name': row['Name'], 'Type': 'Batter', 'Data': row})
    
    for idx, row in bowlers.iterrows():
        players.append({'Name': row['Name'], 'Type': 'Bowler', 'Data': row})
    
    for idx, row in allrounders.iterrows():
        players.append({'Name': row['Name'], 'Type': 'All-rounder', 'Data': row})
    
    return players

def fuzzy_search_player(query, player_names, limit=5):
    """Perform fuzzy search on player names"""
    if not query:
        return []
    matches = process.extract(query, player_names, scorer=fuzz.token_set_ratio, limit=limit)
    return [match[0] for match in matches if match[1] > 50]

def get_player_info(player_name, all_players_dict):
    """Get player information"""
    return all_players_dict.get(player_name, None)

def calculate_batter_score(data):
    """Calculate score for a batter"""
    # Year 1: Runs + Strike_rate + avg
    # Year 2: Runs + Strike_rate + avg
    
    cols = list(data.index)
    
    # Handle column names that might vary
    score = 0
    
    # Get all numeric columns (skip 'Name' and 'Type' if present)
    numeric_data = pd.to_numeric(data, errors='coerce')
    
    # Sum all numeric values, treating NaN as 0
    score = numeric_data.sum(skipna=True)
    
    return score

def calculate_bowler_score(data):
    """Calculate score for a bowler
    wickets*25 + (169/economy) + avg*2.5
    """
    score = 0
    
    # Get indices of columns
    cols = list(data.index)
    
    # Identify pattern: wickets, economy, bowling avg repeats twice (for 2 years)
    # Pattern: wickets, economy, bowling avg, wickets, economy, bowling avg
    
    numeric_data = pd.to_numeric(data, errors='coerce').fillna(0)
    
    # Extract wickets, economy, bowling avg for both years
    # Assuming format: [wickets1, economy1, bowling_avg1, wickets2, economy2, bowling_avg2]
    
    wickets = []
    economy = []
    bowling_avg = []
    
    for i, val in enumerate(numeric_data):
        if i % 3 == 0:  # wickets columns
            wickets.append(val)
        elif i % 3 == 1:  # economy columns
            economy.append(val)
        else:  # bowling avg columns
            bowling_avg.append(val)
    
    # Calculate score
    for w, e, a in zip(wickets, economy, bowling_avg):
        score += w * 25
        # Handle division by zero for economy
        if e != 0:
            score += 169 / e
        score += a * 2.5
    
    return score

def calculate_allrounder_score(data):
    """Calculate score for an all-rounder
    wickets*25 + (169/economy) + avg*2.5 + Runs + Strike_rate + avg
    """
    score = 0
    
    numeric_data = pd.to_numeric(data, errors='coerce').fillna(0)
    
    # For all-rounders: [Runs1, SR1, avg1, wickets1, economy1, bowling_avg1, Runs2, SR2, batting_avg2, wickets2, economy2, bowling_avg2]
    # Pattern repeats, need to handle batting and bowling stats separately
    
    # Sum all and apply formulas - this is complex, let me simplify
    # We need to identify which columns are which
    
    # For now, let's calculate based on position in array
    values_list = list(numeric_data)
    
    # Assuming: batting stats (Runs, SR, avg) x2, bowling stats (wickets, economy, bowling_avg) x2
    if len(values_list) >= 12:
        # Year 1
        runs_1 = values_list[0] if not pd.isna(values_list[0]) else 0
        sr_1 = values_list[1] if not pd.isna(values_list[1]) else 0
        bat_avg_1 = values_list[2] if not pd.isna(values_list[2]) else 0
        wickets_1 = values_list[3] if not pd.isna(values_list[3]) else 0
        economy_1 = values_list[4] if not pd.isna(values_list[4]) else 0
        bowl_avg_1 = values_list[5] if not pd.isna(values_list[5]) else 0
        
        # Year 2
        runs_2 = values_list[6] if not pd.isna(values_list[6]) else 0
        sr_2 = values_list[7] if not pd.isna(values_list[7]) else 0
        bat_avg_2 = values_list[8] if not pd.isna(values_list[8]) else 0
        wickets_2 = values_list[9] if not pd.isna(values_list[9]) else 0
        economy_2 = values_list[10] if not pd.isna(values_list[10]) else 0
        bowl_avg_2 = values_list[11] if not pd.isna(values_list[11]) else 0
        
        # Year 1 score
        score += runs_1 + sr_1 + bat_avg_1  # Batting
        score += wickets_1 * 25 + bowl_avg_1 * 2.5  # Bowling
        if economy_1 != 0:
            score += 169 / economy_1
        
        # Year 2 score
        score += runs_2 + sr_2 + bat_avg_2  # Batting
        score += wickets_2 * 25 + bowl_avg_2 * 2.5  # Bowling
        if economy_2 != 0:
            score += 169 / economy_2
    
    return score

def calculate_player_score(player_info, player_type):
    """Calculate individual player score based on type"""
    data = player_info['Data'].drop(['Name', 'Type']) if 'Type' in player_info['Data'].index else player_info['Data'].drop('Name')
    
    if player_type == 'Batter':
        return calculate_batter_score(data)
    elif player_type == 'Bowler':
        return calculate_bowler_score(data)
    elif player_type == 'All-rounder':
        return calculate_allrounder_score(data)
    return 0

def load_teams():
    """Load teams from JSON file"""
    if TEAMS_JSON.exists():
        with open(TEAMS_JSON, 'r') as f:
            return json.load(f)
    return {}

def save_teams(teams):
    """Save teams to JSON file"""
    with open(TEAMS_JSON, 'w') as f:
        json.dump(teams, f, indent=2)

def calculate_team_score(team_players, all_players_dict):
    """Calculate total score for a team"""
    total_score = 0
    player_scores = {}
    
    for player_name in team_players:
        player_info = get_player_info(player_name, all_players_dict)
        if player_info:
            score = calculate_player_score(player_info, player_info['Type'])
            total_score += score
            player_scores[player_name] = score
    
    return total_score, player_scores

# ==================== STREAMLIT UI ====================

st.title("🏏 IPL Team Scorer Dashboard")
st.markdown("Create teams and calculate their performance scores!")

# Load player data
batters, bowlers, allrounders = load_player_data()
all_players = get_all_players_list(batters, bowlers, allrounders)
all_players_dict = {player['Name']: player for player in all_players}
player_names = [player['Name'] for player in all_players]

# Sidebar for team creation
with st.sidebar:
    st.header("⚙️ Team Management")
    
    teams = load_teams()
    
    # New team creation
    st.subheader("Create New Team")
    new_team_name = st.text_input("Team Name", placeholder="e.g., Mumbai Warriors")
    
    if new_team_name and new_team_name not in teams:
        if st.button("Create Team"):
            teams[new_team_name] = []
            save_teams(teams)
            st.success(f"Team '{new_team_name}' created!")
            st.rerun()
    
    # Select team to manage
    if teams:
        selected_team = st.selectbox("Select Team to Manage", list(teams.keys()))
        
        col_del_1, col_del_2 = st.columns([3, 1])
        with col_del_1:
            st.write("Delete selected team")
        with col_del_2:
            if st.button("🗑️ Delete", key="delete_team"):
                teams.pop(selected_team, None)
                save_teams(teams)
                st.success(f"Team '{selected_team}' deleted!")
                st.rerun()
        
        st.subheader(f"Add Players to {selected_team}")
        
        # Fuzzy search input
        search_query = st.text_input("Search player by name", placeholder="Type player name...")
        
        if search_query:
            matching_players = fuzzy_search_player(search_query, player_names, limit=10)
            if matching_players:
                selected_player = st.selectbox(
                    "Select a player",
                    matching_players,
                    key="player_selector"
                )
                
                if selected_player:
                    player_info = get_player_info(selected_player, all_players_dict)
                    if player_info:
                        st.write(f"**Type**: {player_info['Type']}")
                        
                        if st.button("Add Player to Team"):
                            if selected_player not in teams[selected_team]:
                                teams[selected_team].append(selected_player)
                                save_teams(teams)
                                st.success(f"Added {selected_player}!")
                                st.rerun()
                            else:
                                st.warning("Player already in team!")
        
        # Display current team
        st.subheader(f"Current Team ({len(teams[selected_team])} players)")
        if teams[selected_team]:
            for player in teams[selected_team]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    player_type = get_player_info(player, all_players_dict)['Type']
                    st.write(f"👤 {player} ({player_type})")
                with col2:
                    if st.button("❌", key=f"remove_{player}"):
                        teams[selected_team].remove(player)
                        save_teams(teams)
                        st.rerun()
        else:
            st.info("No players in team yet. Search and add players above!")

# Main content area
st.subheader("📊 Team Leaderboard")

if teams:
    # Calculate scores for all teams
    team_scores = []
    
    for team_name, team_players in teams.items():
        if team_players:  # Only calculate if team has players
            total_score, player_scores = calculate_team_score(team_players, all_players_dict)
            team_scores.append({
                'Team': team_name,
                'Players': len(team_players),
                'Score': total_score
            })
    
    if team_scores:
        # Sort by score
        team_scores_df = pd.DataFrame(team_scores).sort_values('Score', ascending=False).reset_index(drop=True)
        team_scores_df.index = team_scores_df.index + 1
        team_scores_df.index.name = 'Rank'
        
        # Display as table
        st.dataframe(team_scores_df, use_container_width=True)
        
        # Detailed view
        st.subheader("📋 Team Details")
        
        selected_detail_team = st.selectbox(
            "Select a team to view details",
            team_scores_df['Team'].tolist(),
            key="detail_selector"
        )
        
        if selected_detail_team:
            team_players = teams[selected_detail_team]
            total_score, player_scores = calculate_team_score(team_players, all_players_dict)
            
            st.markdown(f"### {selected_detail_team}")
            st.metric("Total Team Score", f"{total_score:.2f}")
            
            # Display player breakdown
            st.write("**Player Scores:**")
            player_details = []
            for player_name in team_players:
                player_info = get_player_info(player_name, all_players_dict)
                player_details.append({
                    'Player': player_name,
                    'Type': player_info['Type'],
                    'Score': player_scores.get(player_name, 0)
                })
            
            player_df = pd.DataFrame(player_details).sort_values('Score', ascending=False)
            st.dataframe(player_df, use_container_width=True, hide_index=True)
    else:
        st.info("No teams with players yet. Create a team and add players from the sidebar!")
else:
    st.info("No teams created yet. Use the sidebar to create your first team!")

# Footer
st.divider()
st.markdown("""
### Scoring Formula:
- **Batter**: Runs + Strike Rate + Batting Average (both years)
- **Bowler**: (Wickets × 25) + (169 / Economy) + (Bowling Average × 2.5) (both years)
- **All-rounder**: Bowler formula + Batter formula (both years)
- **Note**: Null values are treated as 0
""")
