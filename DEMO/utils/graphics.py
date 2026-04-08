import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def plot_training_data():
    csv_path = "./logs/training_data.csv"
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        print("Please run training first and make sure the CSV was generated.")
        return

    print("Loading training data...")
    df = pd.read_csv(csv_path)

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Prairie King RL Training Analysis (Balanced Strategy)', fontsize=16)

    axs[0, 0].plot(df['episode'], df['total_reward'], alpha=0.7, label='Episode Reward')
    axs[0, 0].plot(df['episode'], df['total_reward'].rolling(50).mean(), 
                   color='red', linewidth=2, label='Moving Average (50)')
    axs[0, 0].set_title('Reward per Episode')
    axs[0, 0].set_xlabel('Episode')
    axs[0, 0].set_ylabel('Total Reward')
    axs[0, 0].legend()
    axs[0, 0].grid(True, alpha=0.3)

    axs[0, 1].plot(df['episode'], df['episode_length'], alpha=0.7)
    axs[0, 1].plot(df['episode'], df['episode_length'].rolling(50).mean(), 
                   color='red', linewidth=2)
    axs[0, 1].set_title('Episode Length (Survival Time)')
    axs[0, 1].set_xlabel('Episode')
    axs[0, 1].set_ylabel('Steps')
    axs[0, 1].grid(True, alpha=0.3)

    axs[1, 0].plot(df['episode'], df['enemies_killed'], alpha=0.7)
    axs[1, 0].plot(df['episode'], df['enemies_killed'].rolling(50).mean(), 
                   color='red', linewidth=2)
    axs[1, 0].set_title('Enemies Killed per Episode')
    axs[1, 0].set_xlabel('Episode')
    axs[1, 0].set_ylabel('Enemies Killed')
    axs[1, 0].grid(True, alpha=0.3)

    level_data = df.groupby('level_reached')['episode'].count()
    axs[1, 1].bar(level_data.index, level_data.values, color='skyblue')
    axs[1, 1].set_title('Number of Episodes per Level')
    axs[1, 1].set_xlabel('Level')
    axs[1, 1].set_ylabel('Episode Count')
    axs[1, 1].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('./logs/training_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

    print("\n" + "="*60)
    print("SUMMARY STATISTICS BY LEVEL")
    print("="*60)
    
    summary = df.groupby('level_reached').agg({
        'total_reward': ['mean', 'max'],
        'episode_length': 'mean',
        'enemies_killed': 'mean',
        'obtained_powerup': 'mean'
    }).round(2)
    
    summary.columns = ['Avg Reward', 'Best Reward', 'Avg Length', 'Avg Kills', 'Powerup Rate']
    print(summary)

    print(f"\nPlot saved as: ./logs/training_analysis.png")

if __name__ == "__main__":
    plot_training_data()