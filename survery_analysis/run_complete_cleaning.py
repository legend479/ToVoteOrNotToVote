"""
COMPLETE VOTER SURVEY CLEANER
==============================
All-in-one script: Converts text to numeric AND cleans the data
"""

import pandas as pd
import sys

# Add path to find our modules
sys.path.append('/home/claude')

from convert_numeric import convert_text_to_numeric
from clean_data import VoterSurveyDataCleaner


def main():
    """Run the complete pipeline."""
    print("\n" + "🎯" * 30)
    print("COMPLETE VOTER SURVEY DATA PIPELINE")
    print("🎯" * 30)
    print("\nThis script will:")
    print("1. Convert your text responses to numeric codes")
    print("2. Clean and validate the data")
    print("3. Generate quality reports")
    
    # Get input file
    filepath = "survey_responses.csv"  # Replace with your input file path
    
    if not filepath:
        print("No file specified. Exiting.")
        return
    
    # Step 1: Convert to numeric
    print("\n" + "=" * 60)
    print("STEP 1: CONVERTING TEXT TO NUMERIC")
    print("=" * 60)
    
    result = convert_text_to_numeric(filepath)
    
    if not result:
        print("Conversion failed. Exiting.")
        return
    
    df_numeric, numeric_filepath = result
    
    # Step 2: Clean the data
    print("\n" + "=" * 60)
    print("STEP 2: CLEANING DATA")
    print("=" * 60)
    
    input("\nPress Enter to continue to data cleaning...")
    
    # Create cleaner with the numeric file
    cleaner = VoterSurveyDataCleaner(numeric_filepath)
    
    # Run cleaning
    output_file = filepath.replace('.csv', '_cleaned.csv')
    
    # Always keep all responses for this use case
    print("\nRunning cleaning pipeline (keeping all non-empty responses)...\n")
    success = cleaner.run_full_cleaning(output_file, remove_flagged=False)
    
    if success:
        print("\n" + "🎉" * 30)
        print("COMPLETE! YOUR DATA IS READY")
        print("🎉" * 30)
        
        print(f"\n📁 FILES CREATED:")
        print(f"1. Numeric version: {numeric_filepath}")
        print(f"2. Cleaned data: {output_file}")
        print(f"3. Report: {output_file.replace('.csv', '_report.txt')}")
        
        print(f"\n📊 RECOMMENDED FILE FOR ANALYSIS:")
        print(f"   👉 {output_file}")
        print(f"\nThis file contains:")
        print("   • Numeric codes (1-5) for all responses")
        print("   • Quality flags for each response")
        print("   • Completeness indicators")
        print("   • All original incomplete responses preserved")


if __name__ == "__main__":
    main()