This folder contains the code for the waveform fitting.
The waveforms are generated from the .ana and .tana files.
Each waveform is fitted individually to find the real peak position using sinc interpolation method. 
To be more efficient it is best to create different folders to store different dates (example a month worth of data) and have duplicates of the code so the code can run in parallel for both FEMB1 and FEMB2 for that month or for different months.
The fitting window is chosen once for each channel and you should be prompted to renew the fitting window every 5 days (it should be consistent every 5 days)
