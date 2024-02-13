import numpy as np
import matplotlib.pyplot as plt

# Define the number of variables
num_vars = 6

# Create a 2D array of values for the initial proposal and adjusted budget
values = np.array([[10, 30, 249, 143, 33, 79],  # Initial proposal
                   [10.4, 30.1, 249.5, 143.4, 33.5, 79.4]])  # Adjusted budget

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# The plot is made circular, so we need to "complete the loop"
# and append the start to the end.
values = np.concatenate((values, values[:,[0]]), axis=1)
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Draw one axe per variable and add labels
labels = ['Design', 'Startup', 'Investment', 'Development', 'Product', 'Business']
labels.append(labels[0])  # Repeat the first label to close the loop

# Set the tick labels and gridlines for the theta axis
ax.set_thetagrids(np.degrees(angles), labels)

# Draw ylabels
ax.set_rscale('log')
ax.set_rlabel_position(0)
plt.yticks([10, 100, 1000, 10000, 100000], ["10", "100", "1k", "10k", "100k"], color="grey", size=7)
plt.ylim(0,300000)

# Plot data
ax.plot(angles, values[0], color='red', linewidth=2, linestyle='solid', label='Initial proposal')
ax.fill(angles, values[0], color='red', alpha=0.25)

ax.plot(angles, values[1], color='blue', linewidth=2, linestyle='solid', label='Adjusted budget')
ax.fill(angles, values[1], color='blue', alpha=0.25)

# Add legend
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

plt.show()
