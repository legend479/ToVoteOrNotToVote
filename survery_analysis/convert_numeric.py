"""
Voter Survey - Text to Numeric Converter
=========================================
Converts text responses to numeric codes based on the survey questionnaire.
Run this BEFORE the cleaning script.
"""

import pandas as pd
import numpy as np

# Define the mapping from text responses to numeric codes
RESPONSE_MAPPINGS = {
    'q1_emotion': {
        'Excitement': 1,
        'Curiosity': 2,
        'Indifference': 3,
        'Frustration': 4,
        'Distrust': 5
    },
    'q2_frequency': {
        'Always': 1,
        'Often': 2,
        'Sometimes': 3,
        'Rarely': 4,
        'Never': 5
    },
    'q3_effort_tradeoff': {
        'Definitely yes': 1,
        'Probably yes': 2,
        'Not sure': 3,
        'Probably not': 4,
        'Definitely not': 5
    },
    'q4_perceived_impact': {
        'Yes, definitely': 1,
        'Maybe somewhat': 2,
        'Not really': 3,
        'Not at all': 4
    },
    'q5_civic_duty': {
        'Strongly agree': 1,
        'Agree': 2,
        'Neutral': 3,
        'Disagree': 4,
        'Strongly disagree': 5
    },
    'q6_emotional_reward': {
        'Proud and satisfied': 1,
        'Relieved or calm': 2,
        'Neutral': 3,
        'Like it didn\'t matter': 4,
        'Regretful or skeptical': 5
    },
    'q7_trust': {
        'Very confident': 1,
        'Somewhat confident': 2,
        'Unsure': 3,
        'Somewhat doubtful': 4,
        'Very doubtful': 5
    },
    'q8_social_influence': {
        'Strongly agree': 1,
        'Agree': 2,
        'Neutral': 3,
        'Disagree': 4,
        'Strongly disagree': 5
    },
    'q9_information_load': {
        'Strongly agree': 1,
        'Agree': 2,
        'Neutral': 3,
        'Disagree': 4,
        'Strongly disagree': 5
    },
    'q10_disillusionment': {
        'Strongly agree': 1,
        'Agree': 2,
        'Neutral': 3,
        'Disagree': 4,
        'Strongly disagree': 5
    },
    'q11_online_voting': {
        'Definitely yes': 1,
        'Probably yes': 2,
        'Not sure': 3,
        'Probably not': 4,
        'Definitely not': 5
    },
    'q12_competitiveness': {
        'Definitely yes': 1,
        'Probably yes': 2,
        'Not sure': 3,
        'Probably not': 4,
        'Definitely not': 5
    },
    'q13_incentive': {
        'A chance to win a small monetary reward (e.g., local prize lottery for voters)': 1,
        'A \'Voter ID badge\' or digital certificate recognizing participation': 2,
        'Social media acknowledgment or a \'Voter\' badge for your profile': 3,
        'Nothing — I\'d vote anyway': 4,
        'None of these would make a difference': 5
    }
}


def convert_text_to_numeric(filepath, output_path=None):
    """
    Convert text responses to numeric codes.
    
    Parameters:
    -----------
    filepath : str
        Path to the CSV file with text responses
    output_path : str, optional
        Path for output file. If None, adds '_numeric' to original filename
    
    Returns:
    --------
    DataFrame with numeric codes
    """
    print("=" * 60)
    print("TEXT TO NUMERIC CONVERTER")
    print("=" * 60)
    
    # Load data (try semicolon delimiter first since that's what your data uses)
    print("\nLoading data...")
    try:
        df = pd.read_csv(filepath, delimiter=';')
        print(f"✓ Loaded {len(df)} responses using semicolon delimiter")
    except:
        try:
            df = pd.read_csv(filepath)
            print(f"✓ Loaded {len(df)} responses using comma delimiter")
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            return None
    
    print(f"  Columns: {len(df.columns)}")
    
    # Create a copy for the numeric version
    df_numeric = df.copy()
    
    # Convert each question column
    print("\nConverting text responses to numeric codes:")
    print("-" * 60)
    
    conversion_stats = {}
    
    for col, mapping in RESPONSE_MAPPINGS.items():
        if col in df.columns:
            # Store original values for reporting
            original_values = df[col].copy()
            
            # Convert to numeric using mapping
            df_numeric[col] = df[col].map(mapping)
            
            # Count conversions
            converted = (~original_values.isna() & ~df_numeric[col].isna()).sum()
            missing_original = original_values.isna().sum()
            unmapped = (~original_values.isna() & df_numeric[col].isna()).sum()
            
            conversion_stats[col] = {
                'converted': converted,
                'missing': missing_original,
                'unmapped': unmapped
            }
            
            print(f"{col}:")
            print(f"  ✓ Converted: {converted}")
            if missing_original > 0:
                print(f"  • Missing in original: {missing_original}")
            if unmapped > 0:
                print(f"  ⚠ Unmapped values: {unmapped}")
                # Show which values couldn't be mapped
                unmapped_vals = original_values[~original_values.isna() & df_numeric[col].isna()].unique()
                print(f"    Values: {unmapped_vals[:5]}")  # Show first 5
        else:
            print(f"{col}: ⚠ Column not found in dataset")
    
    # Show summary
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    
    total_converted = sum(s['converted'] for s in conversion_stats.values())
    total_cells = len(df) * len(RESPONSE_MAPPINGS)
    
    print(f"Total conversions: {total_converted}")
    print(f"Conversion rate: {(total_converted/total_cells)*100:.1f}%")
    
    # Check for any problematic unmapped values
    total_unmapped = sum(s['unmapped'] for s in conversion_stats.values())
    if total_unmapped > 0:
        print(f"\n⚠ Warning: {total_unmapped} values could not be mapped")
        print("  These will be treated as missing data in analysis")
        print("  Review the unmapped values above to check for typos or variations")
    
    # Save the numeric version
    if output_path is None:
        output_path = filepath.replace('.csv', '_numeric.csv')
    
    df_numeric.to_csv(output_path, index=False)
    print(f"\n✓ Saved numeric version to: {output_path}")
    print(f"  You can now use this file with the cleaning script!")
    
    # Show preview
    print("\n" + "=" * 60)
    print("DATA PREVIEW (first 3 rows of converted columns)")
    print("=" * 60)
    preview_cols = ['id', 'q1_emotion', 'q2_frequency', 'q3_effort_tradeoff', 
                   'q4_perceived_impact', 'q5_civic_duty']
    available_cols = [col for col in preview_cols if col in df_numeric.columns]
    print(df_numeric[available_cols].head(3))
    
    return df_numeric, output_path


def main():
    """Main execution function."""
    print("\n" + "🔄" * 30)
    print("VOTER SURVEY TEXT TO NUMERIC CONVERTER")
    print("🔄" * 30)
    print("\nThis script converts your text responses to numeric codes")
    print("Run this BEFORE the data cleaning script!")
    
    filepath = input("\nEnter path to your CSV file: ").strip()
    
    if not filepath:
        print("No file specified. Exiting.")
        return
    
    # Convert the data
    result = convert_text_to_numeric(filepath)
    
    if result:
        df_numeric, output_path = result
        
        print("\n" + "✅" * 30)
        print("CONVERSION COMPLETE!")
        print("✅" * 30)
        
        print("\n📊 NEXT STEPS:")
        print("-" * 60)
        print("1. Review the conversion statistics above")
        print("2. Run the cleaning script with your NEW numeric file:")
        print(f"   python clean_voter_survey.py")
        print(f"   (Use '{output_path}' as input)")
        print("\n3. The numeric codes correspond to:")
        print("   1 = Most positive/frequent")
        print("   5 = Most negative/infrequent")


if __name__ == "__main__":
    main()