# ToVoteOrNotToVote
Project for Introduction to Neuro-Economics (CG4.402) 

![logo](./logo.png)

## Problem Statement
Behavioural Insights into Voter Turnout and Electoral Participation

## Motivation and Core Idea
Voter turnout is a cornerstone of a healthy representative democracy, yet its drivers remain a subject of intense
study. Classical rational choice models, which posit that individuals vote only if the instrumental benefit of affecting the
outcome outweighs the cost, fail to explain why millions of people participate in large-scale elections—a phenomenon
often termed the "paradox of voting"

The core idea of this project is to reframe the voting decision from a purely rational act to a behavioral one, governed
by an individual’s net perceived utility. We posit that a person’s choice to vote or abstain is a function of a wide
array of factors that shape their subjective valuation of the act. This utility is not static but is a dynamic function of
the individual’s personal characteristics (demographics, beliefs, biases) and the specific electoral context (election
competitiveness, media narrative, institutional trust). Our guiding principle is to move beyond explaining the act of
voting and towards understanding the perceived value of the vote itself.

### Author:
Prakhar Singhal
Sativika Miryala
### Professor:
Kavita Vemuri


## Links: 
- [Project Presentation](./presentation.pdf)
- [Project Report](./docs/Project%20Proposal.pdf)
- [Survey Questionnaire](https://vote-mind-map.lovable.app/)
- [Survey Data Dashboard](https://vote-mind-map.lovable.app/dashboard)
- [Agent Based Election Simulation](https://agentic-election-simulator-118267798784.us-west1.run.app/)

## Repository Structure
```
.
├── README.md
├── docs
│   ├── Project Execution Plan.pdf
│   ├── Project Hypothesis and Nudges Ledger.pdf
│   ├── Project Literature Review.pdf
│   ├── Project Proposal.pdf
│   ├── Project Simulation Seup Report.pdf
│   ├── Project Voter Survey Report.pdf
│   ├── hypothesis_nudges.md
│   └── initial_form.md
├── literature_review
│   ├── Candidate Features Influencing Voter Turnout.pdf
│   ├── Determinants of Voter Turnout and Vote Choice_ A Multidisciplinary Review.pdf
│   ├── Voter Turnout_ A Multidisciplinary Review.pdf
│   ├── determinants_of_voter_turnout.md
│   ├── references
│   │   ├── 18.02.015-20160102.pdf
│   │   ├── FactorsInfluencingVotingBehaviour:AComprehensive Literature Review.pdf
│   │   ├── JBEP-6-S1-7.pdf
│   │   ├── Measuring_the _strength_of_voter_turnout_habit.md
│   │   ├── Paradox of Not Voting A Decision Theorectic Analysis.pdf
│   │   ├── bryan-et-al-2011-motivating-voter-turnout-by-invoking-the-self.pdf
│   │   ├── ssrn-4969540.pdf
│   │   └── what-affects-voter-turnout-a-review-articlemeta-analysis-of-aggregate-research.pdf
│   └── summaries_papers.md
├── logo.png
└── survery_analysis
    ├── analysis_guide.txt
    ├── clean_data.py
    ├── comprehensive_analysis.py
    ├── convert_numeric.py
    ├── fix_survey_data.py
    ├── hypothesis_testing.py
    ├── results
    │   ├── analysis.md
    │   ├── hypothesis_tests
    │   │   └── hypothesis_summary.png
    │   ├── output.txt
    │   └── voter_analysis_plots
    │       ├── correlation_heatmap.png
    │       ├── demographic_analysis.png
    │       ├── individual_distributions.png
    │       ├── model_components_correlation.png
    │       └── summary_visualizations.png
    ├── run_complete_cleaning.py
    ├── survey_questions.md
    ├── survey_responses.csv
    ├── survey_responses_cleaned.csv
    ├── survey_responses_cleaned_report.txt
    └── survey_responses_numeric.csv
```
