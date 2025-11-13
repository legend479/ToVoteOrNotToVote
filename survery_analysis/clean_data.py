"""
Voter Motivation Survey - Data Cleaning Script
===============================================
This script cleans survey data while preserving incomplete responses.
It focuses on data quality assessment rather than aggressive removal.

Author: Data Cleaning Pipeline
Date: November 2025
"""

import pandas as pd
import numpy as np
import re
import csv
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class VoterSurveyDataCleaner:
    """
    A comprehensive data cleaning class for voter motivation survey data.
    Preserves incomplete responses while flagging data quality issues.
    """
    
    def __init__(self, filepath):
        """
        Initialize the cleaner with a dataset filepath.
        
        Parameters:
        -----------
        filepath : str
            Path to the CSV file containing survey responses
        """
        self.filepath = filepath
        self.df = None
        self.df_original = None
        self.cleaning_report = {}
        
        # Define column groups
        self.required_cols = [
            'q1_emotion', 'q2_frequency', 'q3_effort_tradeoff', 
            'q4_perceived_impact', 'q5_civic_duty', 'q6_emotional_reward', 
            'q7_trust', 'q8_social_influence', 'q9_information_load', 
            'q10_disillusionment', 'q11_online_voting', 'q12_competitiveness', 
            'q13_incentive'
        ]
        
        self.demographic_cols = ['age_range', 'location']
        self.metadata_cols = ['id', 'created_at']
        self.open_response_col = 'q14_open_response'
        
        # Valid ranges for each question
        self.valid_ranges = {
            'q1_emotion': (1, 5),
            'q2_frequency': (1, 5),
            'q3_effort_tradeoff': (1, 5),
            'q4_perceived_impact': (1, 4),
            'q5_civic_duty': (1, 5),
            'q6_emotional_reward': (1, 5),
            'q7_trust': (1, 5),
            'q8_social_influence': (1, 5),
            'q9_information_load': (1, 5),
            'q10_disillusionment': (1, 5),
            'q11_online_voting': (1, 5),
            'q12_competitiveness': (1, 5),
            'q13_incentive': (1, 5)
        }
        
    def load_data(self):
        """Load the dataset from CSV file with multiple fallback methods."""
        print("=" * 60)
        print("LOADING DATA")
        print("=" * 60)
        
        # Try multiple loading methods
        loading_methods = [
            ("Standard", lambda: pd.read_csv(self.filepath)),
            ("Skip bad lines", lambda: pd.read_csv(self.filepath, on_bad_lines='skip')),
            ("Semicolon delimiter", lambda: pd.read_csv(self.filepath, delimiter=';')),
            ("Semicolon + skip bad lines", lambda: pd.read_csv(self.filepath, delimiter=';', on_bad_lines='skip')),
            ("Tab delimiter", lambda: pd.read_csv(self.filepath, delimiter='\t')),
            ("UTF-8 encoding", lambda: pd.read_csv(self.filepath, encoding='utf-8', on_bad_lines='skip')),
            ("Latin-1 encoding", lambda: pd.read_csv(self.filepath, encoding='latin-1', on_bad_lines='skip')),
            ("Quote handling", lambda: pd.read_csv(self.filepath, quoting=csv.QUOTE_ALL, on_bad_lines='skip')),
        ]
        
        for method_name, method_func in loading_methods:
            try:
                print(f"Trying: {method_name}...", end=" ")
                self.df = method_func()
                print(f"✓ SUCCESS!")
                self.df_original = self.df.copy()
                print(f"✓ Loaded {len(self.df)} responses with {len(self.df.columns)} columns")
                
                # Store initial count
                self.cleaning_report['initial_count'] = len(self.df)
                self.cleaning_report['loading_method'] = method_name
                
                return True
            except FileNotFoundError:
                print(f"✗ Error: File not found at {self.filepath}")
                return False
            except Exception as e:
                print(f"✗ Failed")
                continue
        
        # If all methods failed
        print("\n" + "=" * 60)
        print("❌ COULD NOT LOAD FILE")
        print("=" * 60)
        print("\nThe CSV file has formatting issues. Please run the diagnostic tool first:")
        print("  python diagnose_csv.py")
        print("\nCommon issues:")
        print("  - Inconsistent number of columns")
        print("  - Special characters in data")
        print("  - Mixed delimiters")
        return False
    
    def validate_columns(self):
        """Check if expected columns exist in the dataset."""
        print("\n" + "=" * 60)
        print("VALIDATING COLUMNS")
        print("=" * 60)
        
        all_expected = (self.required_cols + self.demographic_cols + 
                       self.metadata_cols + [self.open_response_col])
        
        missing_cols = [col for col in all_expected if col not in self.df.columns]
        extra_cols = [col for col in self.df.columns if col not in all_expected]
        
        if missing_cols:
            print(f"⚠ Missing expected columns: {missing_cols}")
        else:
            print("✓ All expected columns present")
            
        if extra_cols:
            print(f"ℹ Extra columns found: {extra_cols}")
            
        self.cleaning_report['missing_columns'] = missing_cols
        self.cleaning_report['extra_columns'] = extra_cols
        
    def check_data_types(self):
        """Verify and convert data types where necessary."""
        print("\n" + "=" * 60)
        print("CHECKING DATA TYPES")
        print("=" * 60)
        
        # Convert question columns to numeric
        for col in self.required_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
        # Convert timestamp
        if 'created_at' in self.df.columns:
            self.df['created_at'] = pd.to_datetime(self.df['created_at'], errors='coerce')
            print(f"✓ Converted 'created_at' to datetime")
            
        print("✓ Data type conversions complete")
        
    def check_value_ranges(self):
        """Check for out-of-range values in survey questions."""
        print("\n" + "=" * 60)
        print("CHECKING VALUE RANGES")
        print("=" * 60)
        
        range_issues = {}
        
        for col, (min_val, max_val) in self.valid_ranges.items():
            if col in self.df.columns:
                # Find values outside valid range (excluding NaN)
                invalid_mask = (~self.df[col].isna()) & (
                    (self.df[col] < min_val) | (self.df[col] > max_val)
                )
                invalid_count = invalid_mask.sum()
                
                if invalid_count > 0:
                    range_issues[col] = invalid_count
                    print(f"⚠ {col}: {invalid_count} out-of-range values "
                          f"(valid: {min_val}-{max_val})")
                    
                    # Set invalid values to NaN
                    self.df.loc[invalid_mask, col] = np.nan
                    
        if not range_issues:
            print("✓ All values within expected ranges")
        else:
            print(f"\n✓ Set {sum(range_issues.values())} out-of-range values to NaN")
            
        self.cleaning_report['range_issues'] = range_issues
        
    def assess_completeness(self):
        """Assess response completeness without removing data."""
        print("\n" + "=" * 60)
        print("ASSESSING RESPONSE COMPLETENESS")
        print("=" * 60)
        
        # Count missing values per response
        self.df['missing_count'] = self.df[self.required_cols].isna().sum(axis=1)
        self.df['completeness_rate'] = (
            (len(self.required_cols) - self.df['missing_count']) / 
            len(self.required_cols) * 100
        )
        
        # Flag complete responses
        self.df['is_complete'] = self.df['missing_count'] == 0
        
        # Categorize response quality
        def categorize_quality(missing_count):
            if missing_count == 0:
                return 'Complete'
            elif missing_count <= 3:
                return 'Mostly Complete (>75%)'
            elif missing_count <= 6:
                return 'Partial (50-75%)'
            else:
                return 'Minimal (<50%)'
        
        self.df['response_quality'] = self.df['missing_count'].apply(categorize_quality)
        
        # Print summary
        print("\nCompleteness Distribution:")
        quality_counts = self.df['response_quality'].value_counts()
        for quality, count in quality_counts.items():
            pct = (count / len(self.df)) * 100
            print(f"  {quality}: {count} ({pct:.1f}%)")
            
        print(f"\nAverage completeness rate: {self.df['completeness_rate'].mean():.1f}%")
        
        self.cleaning_report['completeness_distribution'] = quality_counts.to_dict()
        
    def analyze_missing_patterns(self):
        """Analyze which questions have the most missing data."""
        print("\n" + "=" * 60)
        print("MISSING DATA BY QUESTION")
        print("=" * 60)
        
        missing_summary = {}
        
        print(f"\n{'Question':<25} {'Missing':<10} {'%':<8}")
        print("-" * 45)
        
        for col in self.required_cols:
            if col in self.df.columns:
                missing_count = self.df[col].isna().sum()
                missing_pct = (missing_count / len(self.df)) * 100
                missing_summary[col] = {
                    'count': missing_count,
                    'percentage': missing_pct
                }
                print(f"{col:<25} {missing_count:<10} {missing_pct:<8.1f}")
                
        # Demographics
        print("\nDemographic Information:")
        for col in self.demographic_cols:
            if col in self.df.columns:
                missing_count = self.df[col].isna().sum()
                missing_pct = (missing_count / len(self.df)) * 100
                print(f"  {col:<23} {missing_count:<10} {missing_pct:<8.1f}")
                
        # Open response
        if self.open_response_col in self.df.columns:
            missing_count = self.df[self.open_response_col].isna().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            print(f"  {self.open_response_col:<23} {missing_count:<10} {missing_pct:<8.1f}")
            
        self.cleaning_report['missing_by_question'] = missing_summary
        
    def check_straightlining(self):
        """Detect potential straightlining (same answer for all questions)."""
        print("\n" + "=" * 60)
        print("DETECTING STRAIGHTLINING")
        print("=" * 60)
        
        # Calculate unique answers per response
        self.df['unique_answers'] = self.df[self.required_cols].nunique(axis=1)
        
        # Flag possible straightlining (1-2 unique values across all questions)
        self.df['possible_straightlining'] = self.df['unique_answers'] <= 2
        
        straightlining_count = self.df['possible_straightlining'].sum()
        straightlining_pct = (straightlining_count / len(self.df)) * 100
        
        print(f"Responses with ≤2 unique values: {straightlining_count} ({straightlining_pct:.1f}%)")
        
        if straightlining_count > 0:
            print("⚠ These responses may indicate inattentive responding")
            print("  (Keep them but flag for sensitivity analysis)")
        else:
            print("✓ No obvious straightlining detected")
            
        self.cleaning_report['straightlining_count'] = straightlining_count
        
    def clean_open_responses(self):
        """Clean and categorize open-ended responses."""
        print("\n" + "=" * 60)
        print("CLEANING OPEN RESPONSES")
        print("=" * 60)
        
        if self.open_response_col not in self.df.columns:
            print("⚠ Open response column not found")
            return
            
        # Clean whitespace
        self.df[self.open_response_col] = (
            self.df[self.open_response_col]
            .astype(str)
            .str.strip()
            .replace('nan', np.nan)
        )
        
        # Define non-substantive responses
        non_responses = [
            'n/a', 'na', 'none', '-', 'nothing', 'no', 'idk', 
            'i don\'t know', 'not sure', 'unsure', '.'
        ]
        
        # Flag substantive responses
        self.df['q14_has_content'] = ~(
            self.df[self.open_response_col].isna() | 
            self.df[self.open_response_col].str.lower().isin(non_responses) |
            (self.df[self.open_response_col].str.len() < 3)
        )
        
        substantive_count = self.df['q14_has_content'].sum()
        substantive_pct = (substantive_count / len(self.df)) * 100
        
        print(f"Substantive responses: {substantive_count} ({substantive_pct:.1f}%)")
        print(f"Empty/non-substantive: {len(self.df) - substantive_count}")
        
        self.cleaning_report['substantive_open_responses'] = substantive_count
        
    def check_demographics(self):
        """Analyze demographic data completeness."""
        print("\n" + "=" * 60)
        print("DEMOGRAPHIC COMPLETENESS")
        print("=" * 60)
        
        # Flag responses missing both demographics
        self.df['missing_all_demographics'] = (
            self.df['age_range'].isna() & self.df['location'].isna()
        )
        
        missing_both = self.df['missing_all_demographics'].sum()
        
        print(f"Missing both age and location: {missing_both}")
        
        if 'age_range' in self.df.columns:
            print(f"\nAge Range Distribution:")
            age_dist = self.df['age_range'].value_counts().sort_index()
            for age, count in age_dist.items():
                print(f"  {age}: {count}")
                
        if 'location' in self.df.columns:
            print(f"\nLocation Distribution:")
            loc_dist = self.df['location'].value_counts()
            for loc, count in loc_dist.items():
                print(f"  {loc}: {count}")
                
        self.cleaning_report['missing_all_demographics'] = missing_both
        
    def detect_duplicates(self):
        """Detect and flag potential duplicate responses (for information only)."""
        print("\n" + "=" * 60)
        print("DETECTING DUPLICATES")
        print("=" * 60)
        
        # Check for exact duplicates based on survey responses
        duplicate_mask = self.df.duplicated(subset=self.required_cols, keep='first')
        duplicate_count = duplicate_mask.sum()
        
        if duplicate_count > 0:
            print(f"ℹ Found {duplicate_count} potential duplicate responses")
            print("  (Flagging for information only - NOT removing)")
            self.df['is_duplicate'] = duplicate_mask
        else:
            print("✓ No duplicate responses found")
            self.df['is_duplicate'] = False
            
        self.cleaning_report['duplicate_count'] = duplicate_count
        
    def check_response_timing(self):
        """Analyze response timing for suspicious patterns."""
        print("\n" + "=" * 60)
        print("ANALYZING RESPONSE TIMING")
        print("=" * 60)
        
        if 'created_at' not in self.df.columns or self.df['created_at'].isna().all():
            print("⚠ Timestamp data not available")
            return
            
        # Sort by timestamp
        self.df = self.df.sort_values('created_at')
        
        # Calculate time differences
        self.df['time_diff_seconds'] = (
            self.df['created_at'].diff().dt.total_seconds()
        )
        
        # Flag suspiciously fast responses (< 30 seconds between submissions)
        self.df['suspicious_timing'] = (
            self.df['time_diff_seconds'] < 30
        ) & (~self.df['time_diff_seconds'].isna())
        
        suspicious_count = self.df['suspicious_timing'].sum()
        
        if suspicious_count > 0:
            print(f"⚠ Found {suspicious_count} responses submitted < 30s apart")
            print("  These may indicate bot submissions or test data")
        else:
            print("✓ No suspicious timing patterns detected")
            
        self.cleaning_report['suspicious_timing'] = suspicious_count
        
    def identify_removals(self):
        """Identify rows that should be removed (minimal criteria - only empty responses)."""
        print("\n" + "=" * 60)
        print("IDENTIFYING ROWS FOR REMOVAL")
        print("=" * 60)
        
        # Completely empty responses (all survey questions are NaN)
        all_questions_null = self.df[self.required_cols].isna().all(axis=1)
        
        print(f"Completely empty responses: {all_questions_null.sum()}")
        
        # Create removal flag (ONLY for completely empty responses)
        self.df['recommended_for_removal'] = all_questions_null
        
        removal_count = self.df['recommended_for_removal'].sum()
        
        print(f"\nTotal recommended for removal: {removal_count}")
        print(f"Responses to retain: {len(self.df) - removal_count}")
        
        if removal_count == 0:
            print("✓ All responses have at least some data - nothing to remove!")
        
        self.cleaning_report['recommended_removals'] = removal_count
        
    def create_quality_flags(self):
        """Create comprehensive quality flag summary."""
        print("\n" + "=" * 60)
        print("CREATING QUALITY FLAGS")
        print("=" * 60)
        
        quality_flags = []
        
        for idx, row in self.df.iterrows():
            flags = []
            
            if row['recommended_for_removal']:
                flags.append('REMOVE')
            if row.get('is_duplicate', False):
                flags.append('DUPLICATE')
            if row.get('possible_straightlining', False):
                flags.append('STRAIGHTLINING')
            if row.get('suspicious_timing', False):
                flags.append('FAST_RESPONSE')
            if row['missing_all_demographics']:
                flags.append('NO_DEMOGRAPHICS')
            if row['response_quality'] == 'Minimal (<50%)':
                flags.append('LOW_COMPLETION')
                
            quality_flags.append('; '.join(flags) if flags else 'CLEAN')
            
        self.df['quality_flags'] = quality_flags
        
        print("\nQuality Flag Distribution:")
        flag_dist = self.df['quality_flags'].value_counts()
        for flag, count in flag_dist.items():
            print(f"  {flag}: {count}")
            
        print("\nNote: DUPLICATE flag is for information only - duplicates are NOT removed")
            
    def generate_report(self):
        """Generate a comprehensive cleaning report."""
        print("\n" + "=" * 60)
        print("DATA CLEANING SUMMARY REPORT")
        print("=" * 60)
        
        report = f"""
DATASET OVERVIEW
----------------
Initial responses: {self.cleaning_report['initial_count']}
Final responses (after removal): {len(self.df[~self.df['recommended_for_removal']])}
Responses flagged for removal: {self.cleaning_report['recommended_removals']}

COMPLETENESS
------------
Complete responses: {(self.df['response_quality'] == 'Complete').sum()}
Mostly complete (>75%): {(self.df['response_quality'] == 'Mostly Complete (>75%)').sum()}
Partial (50-75%): {(self.df['response_quality'] == 'Partial (50-75%)').sum()}
Minimal (<50%): {(self.df['response_quality'] == 'Minimal (<50%)').sum()}

DATA QUALITY ISSUES
-------------------
Out-of-range values corrected: {sum(self.cleaning_report.get('range_issues', {}).values())}
Possible straightlining: {self.cleaning_report['straightlining_count']}
Potential duplicates (flagged, not removed): {self.cleaning_report['duplicate_count']}
Suspicious timing: {self.cleaning_report.get('suspicious_timing', 0)}

DEMOGRAPHIC DATA
----------------
Missing all demographics: {self.cleaning_report['missing_all_demographics']}

OPEN RESPONSES
--------------
Substantive responses: {self.cleaning_report['substantive_open_responses']}

RECOMMENDATION
--------------
• Keep all responses except completely empty ones (no survey data at all)
• Duplicates are FLAGGED but NOT removed - keep all responses
• Use 'response_quality' for stratified analysis
• Use 'quality_flags' to identify potential issues
• Consider sensitivity analysis excluding 'STRAIGHTLINING' or 'DUPLICATE' responses
• Report sample sizes clearly in all analyses
"""
        
        print(report)
        return report
        
    def save_cleaned_data(self, output_path='cleaned_voter_survey.csv', 
                         remove_flagged=False):
        """
        Save the cleaned dataset.
        
        Parameters:
        -----------
        output_path : str
            Path for the output CSV file
        remove_flagged : bool
            If True, actually remove rows flagged for removal
            If False, keep all rows with quality flags
        """
        print("\n" + "=" * 60)
        print("SAVING CLEANED DATA")
        print("=" * 60)
        
        if remove_flagged:
            df_output = self.df[~self.df['recommended_for_removal']].copy()
            print(f"Removing {self.df['recommended_for_removal'].sum()} flagged responses")
        else:
            df_output = self.df.copy()
            print("Keeping all responses (including flagged ones)")
            
        # Drop temporary analysis columns for cleaner output
        cols_to_drop = ['time_diff_seconds']
        df_output = df_output.drop(columns=[col for col in cols_to_drop 
                                            if col in df_output.columns])
        
        df_output.to_csv(output_path, index=False)
        print(f"✓ Saved {len(df_output)} responses to: {output_path}")
        
        return output_path
        
    def run_full_cleaning(self, output_path='cleaned_voter_survey.csv', 
                         remove_flagged=False):
        """
        Run the complete cleaning pipeline.
        
        Parameters:
        -----------
        output_path : str
            Path for the output CSV file
        remove_flagged : bool
            Whether to actually remove flagged rows
        """
        print("\n" + "🧹" * 30)
        print("VOTER SURVEY DATA CLEANING PIPELINE")
        print("🧹" * 30)
        
        # Execute all cleaning steps
        if not self.load_data():
            return False
            
        self.validate_columns()
        self.check_data_types()
        self.check_value_ranges()
        self.assess_completeness()
        self.analyze_missing_patterns()
        self.check_straightlining()
        self.clean_open_responses()
        self.check_demographics()
        self.detect_duplicates()
        self.check_response_timing()
        self.identify_removals()
        self.create_quality_flags()
        
        # Generate report
        report = self.generate_report()
        
        # Save results
        output_file = self.save_cleaned_data(output_path, remove_flagged)
        
        # Save report
        report_path = output_path.replace('.csv', '_report.txt')
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"✓ Saved cleaning report to: {report_path}")
        
        print("\n" + "✅" * 30)
        print("CLEANING COMPLETE!")
        print("✅" * 30)
        
        return True


def main():
    """
    Main execution function with example usage.
    """
    print("\nVOTER SURVEY DATA CLEANER")
    print("=" * 60)
    print("\nUsage Example:")
    print("-" * 60)
    
    # Example usage
    input_file = input("\nEnter path to your survey CSV file: ").strip()
    
    if not input_file:
        print("\nNo file specified. Using default: 'survey_responses.csv'")
        input_file = 'survey_responses.csv'
        
    # Create cleaner instance
    cleaner = VoterSurveyDataCleaner(input_file)
    
    # Ask about removal preference
    print("\nRemoval Strategy:")
    print("1. Keep ALL responses (recommended - flag issues only)")
    print("2. Remove ONLY completely empty responses (no survey answers at all)")
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    remove_flagged = (choice == '2')
    
    # Run cleaning
    output_file = input_file.replace('.csv', '_cleaned.csv')
    success = cleaner.run_full_cleaning(output_file, remove_flagged)
    
    if success:
        print(f"\n✅ Your cleaned data is ready!")
        print(f"   Data: {output_file}")
        print(f"   Report: {output_file.replace('.csv', '_report.txt')}")
        
        # Show next steps
        print("\n📊 NEXT STEPS:")
        print("-" * 60)
        print("1. Review the cleaning report")
        print("2. Examine the 'quality_flags' column in cleaned data")
        print("3. Note: Duplicates are FLAGGED but NOT removed")
        print("4. For analysis:")
        print("   • Start with 'Complete' responses")
        print("   • Compare with 'Mostly Complete' for robustness")
        print("   • Use pairwise deletion for missing data")
        print("   • Report sample sizes clearly")
        print("5. Consider sensitivity analysis excluding:")
        print("   • 'STRAIGHTLINING' responses")
        print("   • 'DUPLICATE' responses (if needed)")
        print("   • 'FAST_RESPONSE' responses (if needed)")


if __name__ == "__main__":
    main()