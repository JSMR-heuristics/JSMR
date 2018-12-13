The results folder contains the data obtained from each district(wijk).  
Within each folder the results from different algorithms, with each of their resepctive battery set-up folders. These battery set-up are distinguished by:
* fixed: a fixed set and amount of batteries located at pre-established fixed locations
* cluster: a fixed amount and type of batteries, but locations are altered
* configure: variable amount and types of batteries and altered locations

To view the .dat files, you'll have to alter the load_pickle.py file. You do this by opening the file and change the file name at row 130 to the filename of the .dat file you want to view.

Run the load_pickle file within the folder of the .dat file in the commandwindow "python load_pickle.py"
