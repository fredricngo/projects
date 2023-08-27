# Record Linkage 
This project looks at two datasets (zagat, fodors) containing information about restaurants and links them by finding records of matches between the two dataframes. 

## Method 
1. Converted data from zagat.csv and fodors.csv into dfs
2. Use known_links.csv as a training set to identify known matches between the two dfs
3. Create matches and unmatches dfs
4. Utilize the Jaro-Winkler distance to measure similarity between datasets
5. Implement probabilistic record linkage to categorize similarities into "low", "medium", or "high"
6. With 27 possible combninations of low, med, high, we count their occurences in the dataset
7. Tuples are then sorted into 3 groups - 'match_tuples', 'possible_tuples', 'unmatch_tuples'
8. Iterate over potential pairs in datasetse, rank similarities, classify into match, possible match, unmatch
9. Final function ouputs counts of each type, returns detailed lists of matches, possible matches, unmatches
