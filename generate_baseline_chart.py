import matplotlib.pyplot as plt

# Hardcoded optimal baseline data matching `inference.py`
tasks = ['text-phishing-filter', 'voice-clone-triage', 'video-deepfake-auth']
scores = [1.0, 1.0, 1.0] # All optimal

plt.figure(figsize=(8, 6))
bars = plt.bar(tasks, scores, color=['#4caf50', '#2196f3', '#ff9800'])

plt.ylim(0, 1.2)
plt.ylabel('Score (Reward)')
plt.title('Baseline Agent Performance on Cyber-Triage Tasks')

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, str(yval), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('baseline_chart.png')
print("Successfully generated baseline_chart.png")
