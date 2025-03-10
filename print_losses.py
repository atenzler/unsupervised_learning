import matplotlib.pyplot as plt

with open(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\losses\losses.txt", "r") as file:
    losses = [float(line.strip()) for line in file]  # Convert each line to float

# Generate y-values as position indices (starting from 1)
y_values = list(range(1, len(losses) + 1))

# Plot
plt.figure(figsize=(8, 5))
plt.plot(y_values, losses, marker='o', linestyle='-', color='b', label='MAE')

# Labels and title
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error (MAE)')
plt.title('Training Loss Over Epochs')
plt.legend()

# Grid for better visualization
plt.grid(True)

# Show plot
plt.show()