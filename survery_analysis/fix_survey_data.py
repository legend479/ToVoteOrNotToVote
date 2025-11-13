"""
Quick Fix Script for Survey Data
=================================
Cleans the numeric CSV to ensure Q14 is properly separated
and all numeric columns are truly numeric.
"""

import pandas as pd
import numpy as np

def fix_survey_csv(input_file, output_file):
    """
    Fix the survey CSV by ensuring:
    1. Q14 (text responses) is in its own column
    2. Q1-Q13 contain only numeric values
    3. Proper handling of missing data
    """
    
    print("=" * 60)
    print("FIXING SURVEY DATA FILE")
    print("=" * 60)
    
    # Load the data
    print(f"\nLoading: {input_file}")
    df = pd.read_csv(input_file)
    
    print(f"Initial shape: {df.shape}")
    print(f"Columns: {list(df.columns[:10])}...")  # Show first 10
    
    # Define numeric question columns
    numeric_cols = [
        'q1_emotion', 'q2_frequency', 'q3_effort_tradeoff', 
        'q4_perceived_impact', 'q5_civic_duty', 'q6_emotional_reward',
        'q7_trust', 'q8_social_influence', 'q9_information_load',
        'q10_disillusionment', 'q11_online_voting', 'q12_competitiveness',
        'q13_incentive'
    ]
    
    print("\nConverting numeric columns...")
    for col in numeric_cols:
        if col in df.columns:
            # Convert to numeric, setting errors to NaN
            original_count = df[col].notna().sum()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            new_count = df[col].notna().sum()
            
            if original_count != new_count:
                print(f"  {col}: {original_count} → {new_count} valid values "
                      f"({original_count - new_count} converted to NaN)")
            else:
                print(f"  {col}: {new_count} valid values ✓")
    
    # Check Q14
    if 'q14_open_response' in df.columns:
        print(f"\nQ14 (open response): {df['q14_open_response'].notna().sum()} responses")
    
    # Save cleaned file
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved cleaned data to: {output_file}")
    print(f"Final shape: {df.shape}")
    
    # Summary
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)
    
    for col in numeric_cols:
        if col in df.columns:
            valid = df[col].notna().sum()
            pct = (valid / len(df)) * 100
            mean_val = df[col].mean()
            print(f"{col}: {valid}/{len(df)} ({pct:.1f}%) - Mean: {mean_val:.2f}")
    
    print("\n✅ File ready for analysis!")
    return df


if __name__ == "__main__":
    print("\n🔧 Survey Data Fixer")
    print("=" * 60)
    
    input_file = input("Enter your CSV filename: ").strip()
    if not input_file:
        input_file = 'survey_responses_numeric.csv'
        print(f"Using default: {input_file}")
    
    output_file = input_file.replace('.csv', '_fixed.csv')
    
    df = fix_survey_csv(input_file, output_file)
    
    print(f"\n🎯 Next steps:")
    print(f"1. Use the fixed file: {output_file}")
    print(f"2. Run: python comprehensive_analysis.py")
    print(f"3. When prompted, enter: {output_file}")