# IPL Team Scorer Dashboard

A Streamlit-based dashboard for creating IPL teams and calculating their performance scores based on player statistics.

## Features

- ✅ **Fuzzy Search**: Find players easily with intelligent search (typo-tolerant)
- ✅ **Multiple Teams**: Create and manage multiple teams simultaneously
- ✅ **Automatic Scoring**: Calculate team scores based on player performance
- ✅ **Leaderboard**: View ranked teams by total score
- ✅ **Player Details**: Breakdown of individual player scores

## Scoring Formula

### Batter Score
```
Runs + Strike_rate + batting_avg (calculated for both years and summed)
```

### Bowler Score
```
(wickets × 25) + (169 / economy) + (bowling_avg × 2.5) (calculated for both years and summed)
```

### All-rounder Score
```
(wickets × 25) + (169 / economy) + (bowling_avg × 2.5) + Runs + Strike_rate + batting_avg (calculated for both years and summed)
```

**Note**: Null/missing values are treated as 0

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Make sure you have the CSV files in the same directory:
   - `IPL_Auction_2026 - Batters.csv`
   - `IPL_Auction_2026 - Bowlers.csv`
   - `IPL_Auction_2026 - All-rounders.csv`

## Usage

Run the dashboard:
```bash
streamlit run ipl_dashboard.py
```

Then:
1. **Create a Team**: Enter team name in sidebar and click "Create Team"
2. **Add Players**: 
   - Search for players using the fuzzy search bar
   - Select from matching results
   - Click "Add Player to Team"
3. **View Leaderboard**: Main area shows all teams ranked by score
4. **View Details**: Select a team to see individual player score breakdown

## File Structure

```
Event/
├── ipl_dashboard.py                          # Main Streamlit app
├── requirements.txt                          # Python dependencies
├── IPL_Auction_2026 - Batters.csv           # Batter statistics
├── IPL_Auction_2026 - Bowlers.csv           # Bowler statistics
├── IPL_Auction_2026 - All-rounders.csv      # All-rounder statistics
└── teams_data.json                          # Saved teams (auto-generated)
```

## Features Explained

### Fuzzy Search
The search bar uses fuzzy matching to find players even with typos or partial names:
- "virat" → finds "Virat Kohli"
- "dhon" → finds "MS DHONI"
- "warner" → finds "David Warner"

### Team Management
- Create multiple teams with unique names
- Add/remove players from teams
- Teams are automatically saved to `teams_data.json`
- Teams persist between sessions

### Leaderboard
- Real-time score calculation
- Teams ranked by total score (highest first)
- Shows number of players in each team

## Notes

- All player data comes from the provided CSV files
- Only players present in the CSVs can be added to teams
- Teams data is saved locally in JSON format
- Null values in CSV are automatically treated as 0 in calculations
