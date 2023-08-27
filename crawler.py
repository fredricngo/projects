import util
import bs4
import urllib.request
import random


INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'four', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])

def read_verify(url):
    #first removes fragment
    #expects absolute url, if not then uses convert_if_relative
    #for every link that the crawler goes through, will verify that it is a valid url to crawl using read_verify
    if not is_url_ok_to_follow(url, limiting_domain):
        raise ValueError ("URL is not OK to follow")
    else:
        fragmented = util.remove_fragment(url)
        relative_url = util.convert_if_relative_url(fragmented, starting_url)
        if relative_url is None:
            raise ValueError ("URL is not found in the starting url")
        else:
            return relative_url

def course_to_title(course):
    #takes in an absolute url of a course (ANTH, CHEM, etc), converts to soup object and returns a list of its classes in soup form
    program_page = util.get_request(course)
    program_page = bs4.BeautifulSoup(program_page.text, "html5lib")
    titles = program_page.find_all(class_="courseblocktitle")
    return titles

def title_to_text(title):
    #takes in a courseblocktitle, strips down its title and description texts and returns a list of words to choose the index from
    desc = []
    title_text = title.get_text().split(".")
    desc = title.next_sibling.get_text().strip().lower().replace('.', '').replace('Â', '').replace('â\x80\x9c', '').replace('â\x80\x99s', '').replace('â\x80\x9d', '').split()
    split_title = title_text[1].lower().strip().split()
    desc.extend(split_title)
    return desc
   
def indexerv4(url):
    start_request = util.get_request(url)
    read = util.read_request(start_request)
    soup = bs4.BeautifulSoup(read, "html5lib")
    courses = soup.find(id="/thecollege/programsofstudy/") #Locating using programs of study
    courses = map(lambda link: urllib.parse.urljoin(url, link['href']), courses.find_all('a')) #returns a list of absolute_urls using <a tags
    tuple_list = [] #end result that is returned, function will iterate through the list and append tuples to the list
    
    for course in courses:
    #iterating through courses (ANTH, CHEM, etc.), extracting title and their description in list form, as well as choosing an index
        titles = course_to_title(course)
        #ran each course through course_to_title function, returned a list of class titles for that course
        
        for title in titles:
        #for every course title, strip down the description and title to get a list to derive the index from based on the stipulations
            desc_list = []
            desc = title_to_text(title)
            #converts the title and description of a class into a list, whereby we can then derive the index word after filtering
            title_text = title.get_text().split(".")
            append_title = title_text[0].strip().replace("\xa0", " ")
            desc_list = [word for word in desc if word.lower() not in INDEX_IGNORE] #filtering
            append_index = random.choice(desc_list) #index word for the course
            
            subsequences = util.find_sequence(title.parent)
            #for every course, if the courseblockmain of that course (i.e, its corresponding div tag) is the header for a subsequence, then run this subsequence loop
            
            if subsequences:
            #if there are subsequences, does the same code as the "for title in titles" loop but compares the words to the OTHER sequences in the subsequence to filter out words
            
                for subseq in subsequences:
                    subseq_titles = subseq.find_all(class_="courseblocktitle")
                    
                    for subseq_title in subseq_titles:
                        other_words = [] #this list compares the words in the other subsequences to this current subsequence
                        subseq_words = [] #list of current subsequence words
                        filtered_words = []
                        subseq_titletxt = subseq_title.get_text().split(".")
                        subseq_list = subseq_title.next_sibling.get_text().lower().strip().split()
                        subseq_title = subseq_titletxt[0].strip().replace("\xa0", " ")
                        subseq_splittitle = subseq_titletxt[1].strip().lower().split()
                        subseq_list.extend(subseq_splittitle)
                        subseq_words = [word for word in subseq_list if word.lower() not in INDEX_IGNORE]
                        tuple_list.append((subseq_title, append_index))
                        #ensures that each subsequence is mapped to the same word in the header of the subsequence, append_index is saved in the above "for title in titles" loop
                        
                        for other_title in subseq_titles:
                        #getting a list of all the words in every subsequence that is not the current subsequence we're iterating over in the above for loop
                            if other_title != subseq_title:
                            #create a list of words for everything BUT the current subsequence, i.e, all the words from the other subsequences 
                                other_titletxt = other_title.get_text().split(".")
                                other_list = other_title.next_sibling.get_text().strip().split()
                                other_title = other_titletxt[0].strip().replace("\xa0", " ")
                                other_splittitle = other_titletxt[1].strip().lower().split()
                    
                                other_list.extend(other_splittitle)
                                
                                other_list = [word for word in other_list if word.lower() not in INDEX_IGNORE]
                                
                                other_words.extend(other_list)
                                
                        filtered_words = [word for word in subseq_words if word.lower() not in other_words]
                        #comparing the current subsequence's words to the list of words from all of the other subsequences
                        
                        if filtered_words:
                        #sometimes returns empty, so writes a condition for if there are filtered words to choose
                            indexed = random.choice(filtered_words)
                            tuple_list.append((subseq_title, indexed)) #course subsquence is mapped to its unique index

                        
            else: #if there are subsequences, run the subsequence code, otherwise just add the course code like normal
                tuple_list.append((append_title, append_index))
    
    return tuple_list


def go():
    '''
    Crawl the college catalog and generate a list with an index.

    Outputs:
        list with the index
    '''

    starting_url = ("https://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/thecollege/programsofstudy.1.html")
    limiting_domain = "classes.cs.uchicago.edu"
    
    if util.is_url_ok_to_follow(starting_url, limiting_domain):
        return indexerv4(starting_url)
        
    else:
        raise ValueError ("URL not ok to follow")

