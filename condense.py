#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import sys
import os
import scipy.stats as st
import matplotlib.pyplot as plt
import datetime
from dateutil import parser
import networkx as nx


# In[2]:


maildir=sys.argv[1]
#maildir="/Users/surbhiprasad/Enron/maildir"


# In[3]:


#output_feather_path="/Users/surbhiprasad"


# In[4]:


dir_list=os.listdir(maildir) 


# In[5]:


ls_files=[]
subfolders = [ f.path for f in os.scandir(maildir) if f.is_dir() ]
for path, subdirs, files in sorted(os.walk(maildir)):
    for name in files:
        ls_files.append(os.path.join(path, name))


# In[6]:


def user(addr):
    if '@enron.com' not in addr:
        return None
    addr = addr[0:addr.index('@')]
    if '<' in addr or '#' in addr or "/o" in addr:
        return None
    if "'" in addr:
        addr = addr.replace("'", "")
    if len(addr)>0 and addr[0] == '.':
        addr = addr[1:]
    if len(addr)==0:
        return None
    return addr


# In[7]:


i=0
def parse_clean_msg(contents,index_mail,filname):
    emails=[]
    if contents.find('\nDate:')!=-1:
        start_key=contents.find('\nDate:')+7
        end_value=contents.find('\nFrom:')
        date_ls=contents[start_key:end_value]
        new_date_ls= parser.parse(date_ls)
        new_date_ls_2=new_date_ls.strftime("%Y-%m-%d")
    else:
        date_ls=None
    if contents.find('\nFrom:')!=-1:
        start_key=contents.find('\nFrom:')+7
        end_value=contents.find('\nTo:')
        from_ls=contents[start_key:end_value].strip(" ")
        cleaned_from_ls=user(from_ls)
    else:
        cleaned_from_ls=None
    if contents.find('\nTo:')!=-1:
        start_key=contents.find('\nTo:')+5
        end_value=contents.find('\nSubject:')
        to_ls=contents[start_key:end_value]
        to_intd_ls=to_ls.replace("\n\t", "")
        new_to_ls=to_intd_ls.split(",")
        cleaned_ls=[user(i.strip(" ")) for i in new_to_ls]
        cleaned_ls = list(filter(None, cleaned_ls))
    else:
        cleaned_ls=None
    #print(len(cleaned_ls))
    start_key=contents.find('\nSubject:')+10
    sub_ls=contents[start_key:].split("\n")[0]
    
    if date_ls==None or cleaned_ls==None or cleaned_from_ls==None:
        emails=[]
    elif len(date_ls)==0 or len(cleaned_ls)==0 or len(cleaned_from_ls)==0:
        emails=[]
    else:
        recipients=len(cleaned_ls)
        for len_ls in range(recipients):
            if  cleaned_ls[len_ls]==None:
                continue
            else:
                emails.append((index_mail,new_date_ls_2,cleaned_from_ls,cleaned_ls[len_ls],recipients,sub_ls,filname))
    return emails


# In[8]:


final_emails=[]
j=0
for dir_name in ls_files:
    #j+=1
    #if j%10000==0:
        #print(j)
    contents = ""
    if (dir_name.rsplit('/', 1)[-1]).startswith('.'): 
        continue
    else:
        with open(dir_name, "r",encoding='latin1') as f:
                            s = f.read()
                            contents += " " 
                            contents += s
                            #contents = contents.lower()
        if len(parse_clean_msg(contents,1,"0"))==0:
            final_emails=final_emails
        else:
            i=i+1
            mailid=i
            filname=dir_name[(dir_name.find("/maildir/")+9):]
            [final_emails.append(br) for br in parse_clean_msg(contents,mailid,filname)]


# In[9]:


df_test = pd.DataFrame(final_emails, columns=['MailID', 'Date','From','To','Recipients','Subject',"filename"])
df_test['Date'] = pd.to_datetime(df_test['Date'])


# In[10]:


df_test.to_feather("enron.feather")

