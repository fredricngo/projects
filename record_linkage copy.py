#DATA 120: Linking restaurant records in Zagat and Fodor's data sets
#FREDRIC NGO


import numpy as np
import pandas as pd
import jellyfish
import util
import itertools
from collections import Counter

#Part 1:
#Create a pandas dataframe for each dataset consisting of four columns
#Restaurant name, city, address

zagat_file = "zagat.csv"
fodors_file = "fodors.csv"
known_links = "known_links.csv"

zagat_columns = ["index", "restaurant_name", "city", "address"]
fodors_columns = ["index", "restaurant_name", "city", "address"]
known_columns = ["zagat", "fodors"]

zagat = pd.read_csv(zagat_file, names=zagat_columns)
fodors = pd.read_csv(fodors_file, names=fodors_columns)
knownlinks = pd.read_csv(known_links, names=known_columns)

#Part 2:
#Use a training set of konwn links (known_links.csv)
#For each row, first column = index of Zagat, second column = index of Fodors
#Read dataset into a dataframe of 3 strings (non-index) columns

def zagat_known(knownlinks):
    
    zagatknown_columns = ["zagat_restaurant", "zagat_city", "zagat_address"]
    zagatknown = pd.DataFrame(columns=zagatknown_columns)
    
    for i in knownlinks["zagat"]:
        zagat_restaurant = zagat.loc[(zagat["index"] == i), "restaurant_name"].values[0]
        zagat_city = zagat.loc[(zagat["index"] == i), "city"].values[0]
        zagat_address = zagat.loc[(zagat["index"] == i), "address"].values[0]
        zagatknown.loc[len(zagatknown)] = [zagat_restaurant, zagat_city, zagat_address]
    return zagatknown
    
zagatknown = zagat_known(knownlinks)

def fodors_known(knownlinks):

    fodorsknown_columns = ["fodors_restaurant", "fodors_city", "fodors_address"]
    fodorsknown = pd.DataFrame(columns=fodorsknown_columns)

    for i in knownlinks["fodors"]:
        fodors_restaurant = fodors.loc[(fodors["index"] == i), "restaurant_name"].values[0]
        fodors_city = fodors.loc[(fodors["index"] == i), "city"].values[0]
        fodors_address = fodors.loc[(fodors["index"] == i), "address"].values[0]
        fodorsknown.loc[len(fodorsknown)] = [fodors_restaurant, fodors_city, fodors_address]
    return fodorsknown
    
fodorsknown = fodors_known(knownlinks)

matches = pd.concat([zagatknown, fodorsknown], axis=1)

#Part 3:
#Creating unmatch datasets, random sampling from zagat and fodors

zs = zagat.sample(n=1000, replace = True, random_state = 1234)
fs = fodors.sample(n=1000, replace = True, random_state = 5678)

def zsdf(zs):

    zsdf_columns = ["zs_restaurant", "zs_city", "zs_address"]
    zsdf = pd.DataFrame(columns=zsdf_columns)
    
    for i in zs["index"]:
        zsdf_restaurant = zs.loc[(zs["index"] == i), "restaurant_name"].values[0]
        zsdf_city = zs.loc[(zs["index"] == i), "city"].values[0]
        zsdf_address = zs.loc[(zs["index"] == i), "address"].values[0]
        zsdf.loc[len(zsdf)] = [zsdf_restaurant, zsdf_city, zsdf_address]
    return zsdf

zsdf = zsdf(zs)

def fsdf(fs):

    fsdf_columns = ["fs_restaurant", "fs_city", "fs_address"]
    fsdf = pd.DataFrame(columns=fsdf_columns)
    
    for i in fs["index"]:
    
        fsdf_restaurant = fs.loc[(fs["index"] == i), "restaurant_name"].values[0]
        fsdf_city = fs.loc[(fs["index"] == i), "city"].values[0]
        fsdf_address = fs.loc[(fs["index"] == i), "address"].values[0]
        fsdf.loc[len(fsdf)] = [fsdf_restaurant, fsdf_city, fsdf_address]

    return fsdf

fsdf = fsdf(fs)

unmatches = pd.concat([zsdf, fsdf], axis=1)


#Part 4: Jaro-Winkler Scores
#Using the Jaro-Winkler distance between two words to calculate similarity
#Jaro-Winkler distances are broken into specific thresholds, ("low", "med", "high)

#Compute the probability that a tuple (pair of restaurants) in that set is a match

#Iterate through all pairs in matches
#Determine their tuples
#Count frequency of each of the 27 possible tuples for each pair

def zag_tuple(zagatknown):
    zagatknown_columns = ["zagat_restaurant", "zagat_city", "zagat_address"]
    zagtuple = []
    for index, row in zagatknown.iterrows():
        values = tuple(row[zagatknown_columns])
        zagtuple.append(values)
    return zagtuple

zagtuple = zag_tuple(zagatknown)


def fod_tuple(fodorsknown):
    fodorsknown_columns = ["fodors_restaurant", "fodors_city", "fodors_address"]
    fodtuple = []
    for index, row in fodorsknown.iterrows():
        value = tuple(row[fodorsknown_columns])
        fodtuple.append(value)
    return fodtuple

fodtuple = fod_tuple(fodorsknown)

#Creating a list of tuples while calculating the jaro-winkler distance

def matchjarotuples(zagtuple, fodtuple):
    match_jaro_tuples = [ ]
    for zag, fodors in zip(zagtuple, fodtuple):
        zag_name = zag[0]
        fodors_name = fodors[0]
        ndist = jellyfish.jaro_winkler(zag_name, fodors_name)

        zag_city = zag[1]
        fodors_city = fodors[1]
        cdist = jellyfish.jaro_winkler(zag_city, fodors_city)

        zag_addy = zag[2]
        fodors_addy = fodors[2]
        adist = jellyfish.jaro_winkler(zag_addy, fodors_addy)

        match_jaro_tuples.append((ndist, cdist, adist))
    return match_jaro_tuples

match_jaro_tuples = matchjarotuples(zagtuple, fodtuple)


#Running get_jw_category() on the match_jaro_tuples list

match_categories = []
for i,j,k in match_jaro_tuples:
    match_categories.append((util.get_jw_category(i), util.get_jw_category(j), util.get_jw_category(k)))

values = ["low", "medium", "high"]
combinations = list(itertools.product(values, repeat = 3))
combs = []
for comb in combinations:
    combs.append(comb)

matchstr = ["".join(comb) for comb in match_categories]
match_freqcount = Counter(matchstr)

match_missing = [comb for comb in combs if comb not in match_categories]
match_missing_str = ["".join(comb) for comb in match_missing if comb not in match_categories]

#Calculating Unmatch Frequency Count
def zagunmatchtuple(zsdf):
    zag_unmatch_tuple = []
    zsdf_columns = ["zs_restaurant", "zs_city", "zs_address"]
    for index, row in zsdf.iterrows():
        zag_unmatch_values = tuple(row[zsdf_columns])
        zag_unmatch_tuple.append(zag_unmatch_values)
    return zag_unmatch_tuple

zag_unmatch_tuple = zagunmatchtuple(zsdf)

def fodunmatchtuple(fsdf):
    fod_unmatch_tuple = []
    fsdf_columns = ["fs_restaurant", "fs_city", "fs_address"]
    for index, row in fsdf.iterrows():
        fod_unmatch_values = tuple(row[fsdf_columns])
        fod_unmatch_tuple.append(fod_unmatch_values)
    return fod_unmatch_tuple

fod_unmatch_tuple = fodunmatchtuple(fsdf)


#Creating a list of tuples while calculating the jaro-winkler distance


def unmatchjarotuples(zag_unmatch_tuple, fod_unmatch_tuple):
    unmatch_jaro_tuples = []

    for zag, fodors in zip(zag_unmatch_tuple, fod_unmatch_tuple):
        zag_n = zag[0]
        fodors_n = fodors[0]
        n1dist = jellyfish.jaro_winkler(zag_n, fodors_n)

        zag_c = zag[1]
        fodors_c = fodors[1]
        c1dist = jellyfish.jaro_winkler(zag_c, fodors_c)

        zag_a = zag[2]
        fodors_a = fodors[2]
        a1dist = jellyfish.jaro_winkler(zag_a, fodors_a)


        unmatch_jaro_tuples.append((n1dist, c1dist, a1dist))
    return unmatch_jaro_tuples

unmatch_jaro_tuples = unmatchjarotuples(zag_unmatch_tuple, fod_unmatch_tuple)

#Running get_jw_category() on the unmatch_jaro_tuples list

unmatch_categories = []
for i,j,k in unmatch_jaro_tuples:
    unmatch_categories.append((util.get_jw_category(i), util.get_jw_category(j), util.get_jw_category(k)))

unmatchstr = ["".join(comb) for comb in unmatch_categories]
unmatch_freqcount = Counter(unmatchstr)

unmatch_missing = [comb for comb in combs if comb not in unmatch_categories]
unmatch_missing_str = ["".join(comb) for comb in unmatch_missing if comb not in unmatch_categories]

#Part 6: Partition Tuples into match, possible match, and unmatch sets

#Categorizing depends on tolerance for two kinds of errors:
#False positive rate: P(wrongly classify actual unmatch as a match)
#False negative rate: P(wrongly classify actual match as unmatch)

possible_tuples = []
possible_tuples = [comb for comb in match_missing if comb in unmatch_missing]
possible_tuples = ["".join(comb) for comb in possible_tuples]

#Order:
#1. Tuples with u(w) = 0, in order of decreasing m(w)
#3. Tuples with m(w) > 0 and u(w) > 0, in order of decreasing ratio
#4. Tuples with increasing u(w), worst tuples are at the end

ratios = [comb for comb in match_categories if comb in unmatch_categories]
ratios = ["".join((comb)) for comb in ratios]

#only one combination exists in both, "lowmediummedium"

sorted_match_freqcount = match_freqcount.most_common()
sorted_match_relative = [(item[0], item[1]/50) for item in sorted_match_freqcount if item[0] != "lowmediummedium"]

#returns relative frequency for matches (i.e, m(w))

sorted_unmatch_freqcount = sorted(unmatch_freqcount.items(), key=lambda x: x[1], reverse=True)
sorted_unmatch_relative = [(item[0], item[1]/1000) for item in sorted_unmatch_freqcount if item[0] != "lowmediummedium"]

sorted_unmatch_freqcount = sorted_unmatch_freqcount[::-1]

for i, v in enumerate(sorted_match_freqcount):
    if v[0] == ratios[0]:
        numerator = sorted_match_freqcount[i][1]

for i,v in enumerate(sorted_unmatch_freqcount):
    if v[0] == ratios[0]:
        denominator = sorted_unmatch_freqcount[i][1]

lowmediummediumratio = numerator/denominator

match_ranking = [tuple([item[0]]) for item in sorted_match_freqcount if item[0] != "lowmediummedium"]

unmatch_ranking = [tuple([item[0]]) for item in sorted_unmatch_freqcount if item[0] != "lowmediummedium"]

final_ranking = []
final_ranking.extend(match_ranking)
final_ranking.append(('lowmediummedium',))
final_ranking.extend(unmatch_ranking)
final_ranking = ["".join(comb) for comb in final_ranking]

#note that final ranking excludes the 8 possible tuples

#Starting at the first tuple, find last tuple w1 such that the
#cumulative sum of u(w) values is at most (0.005)

sorted_match_uw = [(item[0], 0) for item in sorted_match_freqcount if item[0] != "lowmediummedium"]
sorted_unmatch_uw = [(item[0], item[1]/1000) for item in sorted_unmatch_freqcount]

##First tuple in reverse order

sorted_unmatch_mw = [(item[0], 0) for item in list(reversed(sorted_unmatch_freqcount)) if item[0] != "lowmediummedium"]
sorted_match_mw = [(item[0], item[1]/50) for item in reversed(sorted_match_freqcount)]

def find_matches(mu, lambda_):
    possible_tuples1 = []
    possible_tuples1 = [comb for comb in match_missing if comb in unmatch_missing]
    possible_tuples1 = ["".join(comb) for comb in possible_tuples1]

    def valid_matches(sorted_match_uw, sorted_unmatch_uw):
        match_tuples = []
        false_positive_rate = mu
        #renamed mu just so I know what I'm comparing
        counter = 0
        for i in sorted_match_uw:
            if counter + i[1] >= false_positive_rate:
                match_tuples.append(i)
                break
            else:
                counter += i[1]
                match_tuples.append(i)

        for i in sorted_unmatch_uw:
            if counter + (i)[1] >= false_positive_rate:
                match_tuples.append(i)
                break
            else:
                counter += i[1]
                match_tuples.append(i)
        return match_tuples

    match_tuples = valid_matches(sorted_match_uw, sorted_unmatch_uw)
    match_tuples = [tuple([item[0]]) for item in match_tuples]
    matchtuples = ["".join(comb) for comb in match_tuples]

    def valid_unmatches(sorted_unmatch_uw, sorted_match_uw):
        unmatch_tuples = []
        false_negative_rate = lambda_
        cumsum = 0
        for i in sorted_unmatch_mw:
            if cumsum + i[1] >= false_negative_rate:
                unmatch_tuples.append(i)
                break
            else:
                cumsum += i[1]
                unmatch_tuples.append(i)

        for i in sorted_match_mw:
            if cumsum + (i)[1] >= false_negative_rate:
                unmatch_tuples.append(i)
                break
            else:
                cumsum += i[1]
                unmatch_tuples.append(i)
        return unmatch_tuples

    unmatch_tuples = valid_unmatches(sorted_unmatch_uw, sorted_match_uw)
    unmatch_tuples = [tuple([item[0]]) for item in unmatch_tuples]
    unmatchtuples = ["".join(comb) for comb in unmatch_tuples]

    leftovers = [element for element in final_ranking if ((element not in matchtuples) and (element not in unmatchtuples))]
    crossovers = [element for element in unmatchtuples if element in matchtuples]
    unmatchtuples = [item for item in unmatchtuples if item not in crossovers]
    #prioritizing finding matches, hence the unmatchtuples list
    possible_tuples1.extend(leftovers)

    zagat1 = pd.DataFrame(zagat.drop(columns = ["index"]))
    fodors1 = pd.DataFrame(fodors.drop(columns = ["index"]))

    def zag_tuple1(zagat):
        zagtuple1 = []
        zagat1_columns = ["restaurant_name", "city", "address"]
        for index, row in zagat1.iterrows():
            values = tuple(row[zagat1_columns])
            zagtuple1.append(values)
        return zagtuple1

    def fod_tuple1(fodors1):
        fodtuple1 = []
        fod1_columns = ["restaurant_name", "city", "address"]
        for index, row in fodors1.iterrows():
            values = tuple(row[fod1_columns])
            fodtuple1.append(values)
        return fodtuple1

    zagtuple1 = zag_tuple1(zagat1)
    fodtuple1 = fod_tuple1(fodors1)

    def jarocat(zagentry, fodentry):

        jaro_cat = []
        zname = zagentry[0]
        fname = fodentry[0]
        n = jellyfish.jaro_winkler(zname, fname)

        zcity= zagentry[1]
        fcity = fodentry[1]
        c = jellyfish.jaro_winkler(zcity, fcity)

        zaddy = zagentry[2]
        faddy= fodentry[2]
        a = jellyfish.jaro_winkler(zaddy, faddy)

        jaro_cat.append((util.get_jw_category(n), util.get_jw_category(c), util.get_jw_category(a)))
        jaro_cat = ["".join(comb) for comb in jaro_cat]

        return jaro_cat[0]

    def match_maker(zagtuple1, fodtuple1, matchlist, possiblelist):

        final_columns = ["z_restaurant", "z_city", "z_address", "f_restaurant", "f_city", "f_address"]
        
        match_list = []
        possible_list = []
        unmatch_list = []
        
        for i, zagat_entry in enumerate(zagtuple1):
            for j, fodors_entry in enumerate(fodtuple1):
                combination = jarocat(zagat_entry, fodors_entry)
    
                if combination in matchlist:
                    append_match = []
                    for k in zagat_entry:
                        append_match.append(k)
                    for l in fodors_entry:
                        append_match.append(l)
                    match_list.append(append_match)
                    
                elif combination in possiblelist:
                    append_possible = []
                    for m in zagat_entry:
                        append_possible.append(m)
                    for n in fodors_entry:
                        append_possible.append(n)
                    possible_list.append(append_possible)
                    
                else:
                    append_unmatch = []
                    for o in zagat_entry:
                        append_unmatch.append(o)
                    for p in fodors_entry:
                        append_unmatch.append(p)
                    unmatch_list.append(append_unmatch)
                    
        matches = pd.DataFrame(match_list, columns = final_columns)
        possibles = pd.DataFrame(possible_list, columns = final_columns)
        unmatches = pd.DataFrame(unmatch_list, columns = final_columns)
        
        return matches, possibles, unmatches
        
    matches, possibles, unmatches = match_maker(zagtuple1, fodtuple1, matchtuples, possible_tuples1)
    
    return matches, possibles, unmatches
    
if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.02, 0.02)
    print("found {} matches, {} possible matches, and {} "
          "unmatches".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))
