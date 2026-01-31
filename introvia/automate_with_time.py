# Simple and effective IPL Cricket Team Analyzer
import pandas as pd


player_values = {
    "Shreyas Iyer": 45,
    "Phil Salt": 41,
    "Travis Head": 42,
    "Abhishek Sharma": 43,
    "Nicolas Pooran": 47,
    "Quinton Decock": 32,
    "Yashasvi Jaiswal": 46,
    "Sai Sudarshan": 48,
    "Sanju Samson": 40,
    "Rishabh Pant": 35,
    "Harshit Rana": 37,
    "Arshdeep Singh": 43,
    "Deepak Chahar": 32,
    "Ravi Bishnoi": 25,
    "Bhuvneshwar Kumar": 34,
    "Yash Dayal": 30,
    "Pat cummins": 39,
    "Mohammad Siraj": 35,
    "Kuldeep Yadav": 41,
    "Noor Ahmed": 45,
    "Hardik Pandya": 35,
    "Axar Patel": 39,
    "Krunal Pandya": 38,
    "Ravindra Jadeja": 43,
    "Marcus Stoinis": 41
}

def calculate_team_scores(csv_file_path):
    """
    Read CSV file and calculate team scores
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Lists to store results
        team_scores = []  # List for final results (total scores)
        team_names = []   # List for team names
        timestamps = []   # List for submission timestamps
        team_members = [] # List for team members
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Get team name from 'Team Name' column
                team_name = str(row['Team Name']) if pd.notna(row['Team Name']) else f"Team_{index+1}"
                
                # Get timestamp from 'Timestamp' column
                timestamp = str(row['Timestamp']) if pd.notna(row['Timestamp']) else ""
                
                # Get team members from 'Team members Name' column
                members = str(row['Team members Name (1 leader + 4 Members)']) if pd.notna(row['Team members Name (1 leader + 4 Members)']) else "Not specified"
                
                # Initialize result for this row
                result = 0
                
                # Process player columns specifically according to CSV structure
                # Check CSV columns and use the correct ones
                player_columns = []
                
                # Check for all potential batsman columns
                batsman_columns = [
                    'Select Batsmen(Any 1)',   
                    'Select Batsman (Any 1)',
                    'Select Batsman (Any 1).1'
                ]
                for col in batsman_columns:
                    if col in df.columns:
                        player_columns.append(col)
                
                # Check for all potential bowler columns
                bowler_columns = [
                    'Select Bowler(Any 1)', 
                    'Select Bowler (Any 1)',
                    'Select Bowler(Any 1).1',
                    'Select Bowler (Any 1).1'
                ]
                for col in bowler_columns:
                    if col in df.columns:
                        player_columns.append(col)
                
                # Check for all-rounder column
                if 'Select All-rounder (any 1)' in df.columns:
                    player_columns.append('Select All-rounder (any 1)')
                
                # Calculate score from player selections
                for column in player_columns:
                    if column in df.columns:
                        cell_value = row[column]
                        
                        # Check if cell is not empty
                        if pd.notna(cell_value) and str(cell_value).strip():
                            player_name = str(cell_value).strip()
                            
                            # Look up player in hash map
                            if player_name in player_values:
                                result += player_values[player_name]
                                print(f"Found {player_name}: +{player_values[player_name]} points")
                            else:
                                print(f"Player '{player_name}' not found in hash map")
                
                # Append results to lists
                team_scores.append(result)
                team_names.append(team_name)
                timestamps.append(timestamp)
                team_members.append(members)
                
                print(f"{team_name}: Total Score = {result} (Submitted: {timestamp})")
                print(f"Team Members: {members}")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error processing row {index+1}: {e}")
                team_scores.append(0)
                team_names.append(f"Team_{index+1}")
                timestamps.append("")
                team_members.append("Not specified")
                continue
        
        return team_scores, team_names, timestamps, team_members
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return [], [], [], []



def main():
    # Use the Input.csv file
    csv_file = "output.csv"
    
    print(f"\nProcessing {csv_file}...")
    print("=" * 60)
    
    # Print available columns for debugging
    try:
        df_debug = pd.read_csv(csv_file)
        print("\nCSV Columns available:")
        print(df_debug.columns.tolist())
    except Exception as e:
        print(f"Error reading CSV for debugging: {e}")
    
    # Calculate team scores
    scores, names, timestamps, members = calculate_team_scores(csv_file)
    
    if scores and names:
        print("\n" + "=" * 60)
        print("FINAL RESULTS:")
        print("=" * 60)
        
        # Create results DataFrame
        results_df = pd.DataFrame({
            'Team_Name': names,
            'Total_Score': scores,
            'Timestamp': timestamps,
            'Team_Members': members
        })
        
        # Convert timestamp to pandas datetime for proper sorting
        results_df['Timestamp'] = pd.to_datetime(results_df['Timestamp'], errors='coerce')
        
        # Sort by score (highest first) and then by timestamp (earliest first) for tiebreakers
        results_df = results_df.sort_values(['Total_Score', 'Timestamp'], ascending=[False, True])
        
        # Display sorted results
        print("\nRANKED TEAMS (Sorted by Score and Submission Time):")
        print("-" * 80)
        for i, (index, row) in enumerate(results_df.iterrows()):
            timestamp_str = row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['Timestamp']) else 'N/A'
            print(f"{i+1}. {row['Team_Name']}: {row['Total_Score']} points (Submitted: {timestamp_str})")
            print(f"   Team Members: {row['Team_Members']}")
            print("-" * 80)
        
        # Save results
        results_df.to_csv('team_results_ranked.csv', index=False)
        print(f"\nResults saved to 'team_results_ranked.csv'")
    else:
        print("No data processed.")

if __name__ == "__main__":
    main()