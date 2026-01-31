# Simple and effective IPL Cricket Team Analyzer
import pandas as pd


player_values = {
    "Shreyas Iyer": 25,
    "Phil Salt": 20,
    "Travis Head": 28,
    "Abhishek Sharma": 18,
    "Nicolas Pooran": 22,
    "Quinton Decock": 24,
    "Yashasvi Jaiswal": 26,
    "Sai sudarshan": 16,
    "Sanju Samson": 20,
    "Rishabh Pant": 30,
    "Harshit Rana": 12,
    "Arshdeep Singh": 18,
    "Deepak Chahar": 16,
    "Ravi Bishnoi": 15,
    "Digvesh Rathi": 10,
    "Yash Dayal": 14,
    "Pat cummins": 35,
    "Prasidh Krishna": 18,
    "Kuldeep Yadav": 22,
    "Noor Ahmed": 12,
    "Hardik Pandya": 32,
    "Axar Patel": 32,
    "Krunal Pandya": 20,
    "Ravindra Jadeja": 28,
    "Marcus Stoinis": 24
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
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Get team name from 'Team Name' column
                team_name = str(row['Team Name']) if pd.notna(row['Team Name']) else f"Team_{index+1}"
                
                # Initialize result for this row
                result = 0
                
                # Process player columns specifically according to CSV structure
                player_columns = [
                    'Select Batsmen(Any 1)', 
                    'Select Batsman (Any 1)', 
                    'Select Bowler(Any 1)', 
                    'Select Bowler (Any 1)', 
                    'Select All-rounder (any 1)'
                ]
                
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
                
                print(f"{team_name}: Total Score = {result}")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error processing row {index+1}: {e}")
                team_scores.append(0)
                team_names.append(f"Team_{index+1}")
                continue
        
        return team_scores, team_names
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return [], []



def main():
    # Use the Input.csv file
    csv_file = "Input.csv"
    
    print(f"\nProcessing {csv_file}...")
    print("=" * 60)
    
    # Calculate team scores
    scores, names = calculate_team_scores(csv_file)
    
    if scores and names:
        print("\n" + "=" * 60)
        print("FINAL RESULTS:")
        print("=" * 60)
        
        # Create results DataFrame
        results_df = pd.DataFrame({
            'Team_Name': names,
            'Total_Score': scores
        })
        
        # Sort by score (highest first)
        results_df = results_df.sort_values('Total_Score', ascending=False)
        
        # Display sorted results
        print("\nRANKED TEAMS:")
        print("-" * 60)
        for i, (index, row) in enumerate(results_df.iterrows()):
            print(f"{i+1}. {row['Team_Name']}: {row['Total_Score']} points")
        
        # Save results
        results_df.to_csv('team_results.csv', index=False)
        print(f"\nResults saved to 'team_results.csv'")
    else:
        print("No data processed.")

if __name__ == "__main__":
    main()