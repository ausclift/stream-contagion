import pandas as pd
import matplotlib.pyplot as plt

# Load the file
df = pd.read_csv("sentiment_results/sentiment_results.csv")
df = df[['streamer_sentiment', 'event_size']]
df = df[df['streamer_sentiment'] != 0]

print(df.corr(method='kendall'))

# Create a scatter plot
plt.figure(figsize=(8, 8))
plt.scatter(df['streamer_sentiment'], df['event_size'], alpha=0.7)
plt.title('Sentiment vs. Event Size')
plt.xlabel('Sentiment')
plt.ylabel('Event Size')
plt.grid(True)

'''
# Set same scale for both axes
plt.xlim(0, max(max(df['leader_count']), max(df['follower_count'])))
plt.ylim(0, max(max(df['leader_count']), max(df['follower_count'])))
'''

'''
# Annotate points with individual names
for _, row in df.iterrows():
    plt.text(row['leader_count'], row['follower_count'], row['individual'], fontsize=8, alpha=0.7)
'''

plt.show()
