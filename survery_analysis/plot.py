import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Data from Table XIII
data = {
    'Intervention': [
        'Implementation Intentions', 
        'Linguistic Identity', 
        'Social Norm Campaign', 
        'Competitiveness Info', 
        'Public Accountability', 
        'Monetary Lottery'
    ],
    'Mean Lift (pp)': [17.96, 5.06, 0.10, 0.54, 0.18, -0.70]
}
df = pd.DataFrame(data)
df = df.sort_values('Mean Lift (pp)', ascending=False)

# Create a color palette based on positive or negative values
colors = ['#2ca02c' if x > 0 else '#d62728' for x in df['Mean Lift (pp)']]

# Create the plot
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# Use seaborn for a nice bar plot
sns.barplot(x='Mean Lift (pp)', y='Intervention', data=df, palette=colors, ax=ax)

# Add data labels to the bars
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', padding=5, fontsize=10, color='black')

# Add titles and labels
ax.set_title('Nudge Effectiveness Hierarchy: Average Turnout Lift', fontsize=16, pad=20)
ax.set_xlabel('Mean Turnout Lift (Percentage Points)', fontsize=12)
ax.set_ylabel('') # Y-label is clear from the ticks

# Add a vertical line at x=0 to separate positive/negative
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')

# Adjust layout and save
plt.tight_layout()
plt.savefig('nudge_effectiveness_chart.png', dpi=300)

print("Saved nudge_effectiveness_chart.png")