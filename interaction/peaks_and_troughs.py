import yfinance as yf # This gets our ticker data. I want to find a better data source.
import matplotlib.pyplot as plt # Visualization suite. A better one is Seaborne, but I don't know it as well
import numpy as np # Along with Pandas, this is one of the backbones of scientific computing in Python
import pandas as pd # A convienient data structure with Numpy to make things more readable
from scipy.signal import find_peaks # Finds local maxima and minima

# Import Data
symbol_str = 'SPY' # Let's look at SPY
n_days = 180 # How many days into the past to look?
window_size = 5 # How far apart should Peaks and Troughs be at minimum?

# This bit grabs the history
history = pd.DataFrame(yf.Ticker(symbol_str).history(period=f'{n_days}d')).reset_index()

plt.plot(history['Close'])
plt.xticks(rotation=45)
plt.title(f'{symbol_str} over Time')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# Find peaks and troughs using the find_peaks function from scipy.signal
peaks, _ = find_peaks(history['Close'], distance=window_size)
troughs, _ = find_peaks(-history['Close'], distance=window_size)

# Plot the original time series and the peaks and troughs on the same graph
plt.plot(history['Close'])
plt.scatter(peaks, history.loc[peaks, 'Close'], color='red')
plt.scatter(troughs, history.loc[troughs, 'Close'], color='green')
plt.xticks(rotation=45)
plt.show()
