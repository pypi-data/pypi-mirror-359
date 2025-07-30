import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score

def find_optimal_k(X, k_min=2, k_max=10, plot=True):
    # Prompt user if defaults are not overridden
    if k_min == 2 and k_max == 10:
        try:
            k_min = int(input("Enter minimum value of k (default=2): ") or "2")
            k_max = int(input("Enter maximum value of k (default=10): ") or "10")
        except ValueError:
            print("Invalid input. Using default values k_min=2 and k_max=10.")
            k_min, k_max = 2, 10

    scores = []
    k_range = range(k_min, k_max + 1)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=0)
        labels = kmeans.fit_predict(X)
        score = calinski_harabasz_score(X, labels)
        scores.append(score)

    if plot:
        plt.figure(figsize=(8, 5))
        plt.plot(k_range, scores, marker='o', linestyle='--')
        plt.title('Calinski-Harabasz Score for Optimal k')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('Score')
        plt.xticks(k_range)
        plt.show()

    return k_range[scores.index(max(scores))]

def apply_kmeans(X, k):
    kmeans = KMeans(n_clusters=k, random_state=0)
    return kmeans.fit_predict(X)

def distribute_data_evenly(df, cluster_labels, num_clients, output_prefix='client'):
    df = df.copy()
    df['cluster'] = cluster_labels
    client_data = [[] for _ in range(num_clients)]

    for cluster_id in range(max(cluster_labels) + 1):
        cluster_df = df[df['cluster'] == cluster_id]
        cluster_df = cluster_df.sample(frac=1, random_state=0).reset_index(drop=True)
        chunk_size = len(cluster_df) // num_clients
        for i in range(num_clients):
            start = i * chunk_size
            end = (i + 1) * chunk_size
            client_data[i].append(cluster_df.iloc[start:end])

    for idx, parts in enumerate(client_data):
        client_df = pd.concat(parts).drop('cluster', axis=1)
        client_df.to_csv(f'{output_prefix}{idx + 1}.csv', index=False)
        print(f"Exported {output_prefix}{idx + 1}.csv with {len(client_df)} samples.")
