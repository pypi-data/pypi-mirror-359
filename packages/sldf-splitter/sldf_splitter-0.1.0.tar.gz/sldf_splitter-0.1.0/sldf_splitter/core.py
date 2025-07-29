import pandas as pd

def get_most_variation_column(df):
    return df.var(numeric_only=True).idxmax()

def split_and_sort_by_variation(df, label_column, num_clients=4):
    client_dfs = [[] for _ in range(num_clients)]
    labels = df[label_column].unique()

    for label in labels:
        label_df = df[df[label_column] == label]
        if len(label_df) < num_clients:
            print(f"Warning: Not enough samples for label {label} to split into {num_clients} clients.")
            continue

        sort_column = get_most_variation_column(label_df)
        sorted_df = label_df.sort_values(by=sort_column)

        partition_size = len(sorted_df) // num_clients
        for i in range(num_clients):
            start = i * partition_size
            end = (i + 1) * partition_size if i != num_clients - 1 else len(sorted_df)
            client_dfs[i].append(sorted_df.iloc[start:end])

    return [pd.concat(client_parts) for client_parts in client_dfs]

def save_clients_to_csv(clients, prefix="Client", suffix="SLDF"):
    for i, client_df in enumerate(clients, start=1):
        filename = f"{prefix}{i}_{suffix}.csv"
        client_df.to_csv(filename, index=False)
        print(f"Saved {filename}")
