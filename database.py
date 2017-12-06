import urllib2
import ssl
import re
import math
from elograph import *
#from fight_dictionary import fight_dict
from elo import *
#from victory_method import *
#rom card import *
from bet_functions import *
import numpy
import os.path

class fighter:
    name=''
    age=0
    rating_list=[]
    fight_list=[]
    finish_list=[]
    finish_ratings=[]
    survive_list=[]
    survival_ratings=[]
    def __init__(self,name):
        self.name=name

class fight:
    def __init__(self,opponent,outcome,date,method,decision,odds):
        self.opponent=opponent
        self.outcome=outcome
        self.date=date
        self.method=method
        self.decision=decision
        self.odds=odds
        

def get_age(html):
    age=re.compile('Age:</strong>\n<span>[0-9][0-9]')
    age=age.search(html)
    if age:
        age=age.group(0)
        age=int(age[-2:])
    else:
        return(0)
    return(age)

class rating:
    def __init__(self,number,date):
        self.number=number
        self.date=date

def get_odds(c,html,oddslist):
    if reduce(lambda x,y:x+y,map(lambda z:z.odds,c.fight_list))!=0:
        return(c)
    if html==0: html=get_page("https://www.tapology.com/"+c.name)
    date=re.compile('td class=\'date\'>[0-9][0-9\.]*')
    date=date.search(html)
    if date:
       date=truncate(date.group(0))
       i=html.index(date)
       date=date.split('.')
       date=map(int,date)
       odds=re.compile('Odds: [0-9\-+][0-9]*')
       odds=odds.search(html[i:i+80])
       if odds: 
           odds=odds.group(0)
           odds=odds[6:]
           odds=int(odds)
           oddslist.insert(0,[date,odds])
       get_odds(c,html[i+80:],oddslist)
    fl=c.fight_list
    for x in fl:
        for y in oddslist:
            if x.date==y[0]:
                x.odds=y[1]
    return(map(lambda x:[x.odds,x.opponent],c.fight_list))

def truncate(pat):
    i=pat.index('>')
    pat=pat[i+1:len(pat)]
    return(pat)

def before(d1,d2):
    return((d1[0] < d2[0]) or (d1[0] == d2[0] and d1[1] < d2[1]) or (d1[0] == d2[0] and d1[1] == d2[1] and d1[2] < d2[2]))

def results(query,date):
   html=get_page(query)
   win_list= fightlist(html,[],'result win',1)
   loss_list= fightlist(html,[],'loss result',0)
   draw_list= fightlist(html,[],'draw result',.5)
   fight_list=win_list+loss_list+draw_list
   fight_list=filter(lambda x:before(x[2],date),fight_list)
   fight_list=sorted(fight_list,key=lambda x:x[2])
   return(fight_list)

def fightlist(html,fight_list,pat,n):
   pattern2=re.compile(pat)
   p2=pattern2.search(html)
   if p2:
      q2=p2.group(0)
      i2=html.index(q2)
   
      pattern=re.compile('right\'>[0-9][0-9-]*')
      p=pattern.search(html[i2:len(html)])
      if p:
          method=re.compile('Decision|KO|Submission|Disqual')
          method=method.search(html)
          decision='NA'
          if method: 
              method=method.group(0)
              if method=='Decision':
                  decision=re.compile('Unanimous|Split|Majority')
                  decision=decision.search(html)
                  if decision: decision=decision.group(0)
                  else: decision='NA'
          q=p.group(0)
          i=html.index(q)
          h = html[i+7:i+len(q)]
          html=html[i+7:len(html)]
          h=h.split('-')
          date=re.compile('td class=\'date\'>[0-9][0-9\.]*')
          date=date.search(html)
          date=truncate(date.group(0))
          date=date.split('.')
          h=[map(int,h),n,map(int,date),method,decision]
          fight_list.insert(0,h)
          fightlist(html,fight_list,pat,n)
   return(fight_list)

def get_page(query):
   print(query)
   context = ssl._create_unverified_context()
   response2=urllib2.urlopen(query,context=context)
   html=response2.read()
   return(html)

def get_record(html):
   pattern=re.compile('prorecord\'>[0-9][0-9-]*')
   p=pattern.search(html)
   q=p.group(0)
   i=html.index(q)
   h = html[i+11:i+len(q)]
   return(h)

#generate a list of links to tapology pages of opponents
def get_fight_links(html,fight_links,pat,n):
   pattern=re.compile(pat)
   p=pattern.search(html)
   if p:
      q=p.group(0)
      i=html.index(q)
      html = html[i+10:len(html)]
      pattern=re.compile('fightcenter/fighters/.*\"')
      p2=pattern.search(html)
      if p2: 
         q=p2.group(0)
         if html.index(q) < 500:
             q=q[0:len(q)-1]
             method=re.compile('Decision|KO|Submission|Disqual')
             method=method.search(html)
             decision='NA'
             if method: 
                 method=method.group(0)
                 if method=='Decision':
                     decision=re.compile('Unanimous|Split|Majority')
                     decision=decision.search(html)
                     if decision: decision=decision.group(0)
                     else: decision='NA'
             date=re.compile('td class=\'date\'>[0-9][0-9\.]*')
             date=date.search(html)
             date=date.group(0)
             i=html.index(date)
             date=truncate(date)
             date=date.split('.')
             date=map(int,date)
             odds=re.compile('Odds: [0-9\-+][0-9]*')
             odds=odds.search(html[i:i+80])
             if odds: 
                 odds=odds.group(0)
                 odds=odds[6:]
                 odds=int(odds)
             else:
                 odds=0
             fight_links.insert(0,fight("https://www.tapology.com/"+q,n,date,method,decision,odds))
      get_fight_links(html,fight_links,pat,n)
   return(fight_links)

def get_win_links(html):
    obscure=get_fight_links(html,[],'td class=\'win\'',1)
    return(get_fight_links(html,[],'result win',1)+obscure)

def get_loss_links(html):
    obscure=get_fight_links(html,[],'td class=\'loss\'',0)
    return(get_fight_links(html,[],'loss result',0)+obscure)

def get_draw_links(html):
    obscure=get_fight_links(html,[],'td class=\'draw\'',.5)
    return(get_fight_links(html,[],'draw result',.5)+obscure)

def fight_links(html):
    fightlinks=get_win_links(html)+get_loss_links(html)+get_draw_links(html)
    return(fightlinks)
   
#score_list will have form [[1120,1,date],[1050,0,date],...] */
def fighter_rating(score_list): 
    score_list=sorted(score_list,key=lambda x:x[2])
    score_list.insert(0,1000)
    return(reduce(new_rating,score_list)) 


#fight_links gets the links to the pages of the fighters the fighter has fought and puts them in a list of form [[fighter_page,result,date],...,]
#list_rating goes through and converts each page into an Elo rating, based on the record of the opponents, with all these opponents assumed to have a rating of 1000
#fighter rating then reduces this list to an Elo rating
#first step to improved accuracy--when converting pages to Elo ratings in list_rating, which is done by getting record lists, stop when fight dates conflict
def address_rating(address):
    #if address[25:] in fight_dict:
    #    return(fight_dict[address[25:]])
    h=get_page(address)
    f=fight_links(h)
    lr = list_rating(f)
    return(fighter_rating(lr))


def date_rating(address,date):
    h=get_page(address)
    f=fight_links(h)
    f=filter(lambda x:before(x[2],date),f)
    lr = list_rating(f)
    lr=sorted(lr,key=lambda x:x[2])
    return(fighter_rating(lr))


def es(f1,f2):
    return(expected_score(address_rating(f1),address_rating(f2)))


def deep_rating(address):
    h=get_page(address)
    f=fight_links(h)
    lr=map(lambda x:[date_rating(x[0],x[2]),x[1],x[2]],f)
    lr=sorted(lr,key=lambda x:x[2])
    return(fighter_rating(lr))

def decision_modify(l):
    wd={'Unanimous':1,'Split':.66,'Majority':.83,'NA':'NA'}
    ld={'Unanimous':0,'Split':.33,'Majority':.16,'NA':'NA'}
    for x in l:
        if x.outcome==1:
            if x.method=='Decision' and x.decision!='NA':
                x.outcome=wd[x.decision]
        if x.outcome==0:
            if x.method=='Decision' and x.decision!='NA':
                x.outcome=ld[x.decision]
    #l=filter(lambda x:x.method!='Disqual',l)
    return(l)

def finish_modify(l):
    for x in l:
        if x[3]=='Decision':
            x[1]=0
    l=filter(lambda x:x[3]!='Disqual',l)
    return(l)

def survive_modify(l):
    for x in l:
        if x[3]=='Decision':
            x[1]=1
    l=filter(lambda x:x[3]!='Disqual',l)
    return(l)

def win_prob(f1,f2):
    return(expected_score(calc(f1,'win'),calc(f2,'win')))

def finish_prob(f1,f2):
    f1_rating=calc(f1,'win')
    f2_rating=calc(f2,'win')
    finish_rating=calc(f1,'finish')
    survival_rating=calc(f2,'survive')
    expected_finish=expected_score(finish_rating,f2_rating)
    expected_survival=expected_score(f1_rating,survival_rating)
    print(expected_finish,expected_survival)
    return((expected_finish+expected_survival) / 2)

def distance(f1,f2):
    return(1-(finish_prob(f1,f2)+finish_prob(f2,f1)))

def deep_rate(address):
    h=get_page(address)
    f=fight_links(h)
    fighter_list=map(lambda x:x.name,fight_database)
    calculated=filter(lambda x:x[0][25:] in fighter_list,f)
    not_calculated=filter(lambda x:not(x[0][25:] in fighter_list),f)
    calculated=map(lambda x:[check_rating(x.opponent,x.date),x.outcome,x.date],calculated)
    not_calculated=map(lambda x:[rate(x.opponent,x.date),x.outcome,x.date],not_calculated)
    lr=calculated+not_calculated
    lr=sorted(lr,key=lambda x:x.date)
    return(fighter_rating(lr))

def calc(address):
    h=get_page(address)
    f=fight_links(h)
    fighter_list=map(lambda x:x.name,fight_database)
    not_calculated=filter(lambda x:not(x.opponent[25:] in fighter_list),f)
    map(lambda x:[rate(x.opponent,x.date,'win'),x.outcome,x.date],not_calculated)
    return(rt(address,'win'))

def deep_calc(address):
    h=get_page(address)
    f=fight_links(h)
    map(lambda x:calc(x[0]),f)
    rt(address)

#Always rerate input fighter, so as to update continually
def rate(address,date,query):
    print(query)
    c=fighter(address[25:])
    if query=='win':
        c.fight_list=[]
        c.rating_list=[]
    if query=='finish':
        c.finish_list=[]
        c.finish_ratings=[]
    if query=='survive':
        c.survive_list=[]
        c.survival_ratings=[]
    print('\033[1;31;40m \n')
    h=get_page(address)
    print('\033[1;37;40m ')
    print("Opponents:")
    if query=='win':
        f=decision_modify(fight_links(h))
    if query=='finish':
        f=finish_modify(fight_links(h))
    if query=='survive':
        f=survive_modify(fight_links(h))
    f=sorted(f,key=lambda x:x.date)
    lr = list_rating(f)
    if lr==[]: return(1000)
    lr=sorted(lr,key=lambda x:x[2])
    lr.insert(0,1000)
    rating_list=[]
    print('\033[1;32;40m ')
    for i in range(1,len(lr)+1):
        if isinstance(lr[i-1],int):
            a=[1000,[1900,1,1]]
        else:
            a=[reduce(new_rating,lr[0:i]),lr[i-1][2]]
        #print(a)
        graph_list([a[0]])
        rating_list.insert(0,a) 
    print('\033[1;37;40m ')
    rating_list.reverse()
    for r in rating_list:
        e=rating(r[0],r[1])
        if query=='win':
            c.rating_list.insert(0,e)
        if query=='finish':
            c.finish_ratings.insert(0,e)
        if query=='survive':
            c.survival_ratings.insert(0,e)
    for fight in f:
        if query=='win':
            c.fight_list.insert(0,fight)
        if query=='finish':
            c.finish_list.insert(0,fight)
        if query=='survive':
            c.survive_list.insert(0,fight)
    if query=='win':
        c.rating_list=sorted(c.rating_list,key=lambda x:x.date)
        add_fighter(c)
        save_database()
    if query=='finish':
        c.finish_ratings=sorted(c.finish_ratings,key=lambda x:x.date)
        return(c.finish_ratings[-1].number)
    if query=='survive':
        c.survival_ratings=sorted(c.survival_ratings,key=lambda x:x.date)
        return(c.survival_ratings[-1].number)
    return(closest(c,date))

def rerate(fighter):
    print(fighter.name)
    date=[2020,1,1]
    c=fighter
    c.rating_list=[]
    #print('\033[1;37;40m ')
    #print("Opponents:")
    f=c.fight_list
    f=sorted(f,key=lambda x:x.date)
    lr = relist_rating(f)
    if lr==[]: return(1000)
    lr=sorted(lr,key=lambda x:x[2])
    lr.insert(0,1000)
    rating_list=[]
    #print('\033[1;32;40m ')
    for i in range(1,len(lr)+1):
        if isinstance(lr[i-1],int):
            a=[1000,[1900,1,1]]
        else:
            a=[reduce(new_rating,lr[0:i]),lr[i-1][2]]
        #print(a)
        #graph_list([a[0]])
        rating_list.insert(0,a) 
    #print('\033[1;37;40m ')
    rating_list.reverse()
    for r in rating_list:
        e=rating(r[0],r[1])
        c.rating_list.insert(0,e)
    c.rating_list=sorted(c.rating_list,key=lambda x:x.date)
    return(closest(c,date))

#We have problem that before([date]) eliminates most recent fight (prior to excluded fight) which we want to include. Why would it though?  The most recent fight is before the date which is input. 
#Problem is that previous ratings are associated with next fights
def closest(c,date):
    ratings=filter(lambda x:before(x.date,date),c.rating_list)
    if len(ratings) > 0:
        closest_rating=ratings[-1]
        return(closest_rating.number)
    else:
        return(1000)

def rate1(address,date):
    h=get_page(address)
    f=fight_links(h)
    f=filter(lambda x:before(x[2],date),f)
    lr = list_rating(f)
    lr=sorted(lr,key=lambda x:x[2])
    return(fighter_rating(lr))

def rt(address,query):
    return(rate(address,[2020,1,1],query))

def check_rating(address,date):
    fighter_list=filter(lambda x: x.name==address[25:], fight_database)
    if len(fighter_list)==1:
        c=fighter_list[0]
        if not(isinstance(map(lambda x:x.date,c.rating_list)[0],list)):
            correct(c)
        return(closest(c,date))
    else:
        return(rate1(address,date))

def get_fighter(address):
    fighter_list=filter(lambda x: x.name==address[25:], fight_database)
    if len(fighter_list)==1:
        return(fighter_list[0])
    else:
        return(False)

def correct(c):
    c.rating_list=map(lambda x:rating(x.date,x.number),c.rating_list)
    
def so_record(address):
    h=get_page(address)
    f=fight_links(h)
    f=map(lambda x:results(x[0],[2020,20,20]),f)
    for i in f:
        i=10
    print(f)

def is_finish(s):
    return(s=='Submission' or s=='KO')

#results gives win_list+loss_list+draw_list
def list_rating(li):
    #to change list_rating, divide li into two lists--one for ratings that have already been calculated, one for ratings that have not.
    calculated=filter(in_database,li) 
    calculated=map(lambda x: [check_rating(x.opponent,x.date),x.outcome,x.date,x.method],calculated)
    not_calculated=filter(lambda x:not(in_database(x)),li)
    #Results turns each fight link into a record-[w,l,d]--which is used to give an approximate Elo rating for each uncalculated opponent.
    not_calculated=map(lambda x: [record_rating(results(x.opponent,x.date)),x.outcome,x.date,x.method],not_calculated)
    li=calculated+not_calculated
    if len(li) > 0: print(str(int(100*float(len(calculated))/len(li)))+"% of opponents in database.")
    li=sorted(li,key=lambda x:x[2])
    return(li)

def relist_rating(li):
    #to change list_rating, divide li into two lists--one for ratings that have already been calculated, one for ratings that have not.
    calculated=filter(in_database,li) 
    calculated=map(lambda x: [check_rating(x.opponent,x.date),x.outcome,x.date,x.method],calculated)
    not_calculated=filter(lambda x:not(in_database(x)),li)
    #Results turns each fight link into a record-[w,l,d]--which is used to give an approximate Elo rating for each uncalculated opponent.
    not_calculated=map(lambda x: [1000,x.outcome,x.date,x.method],not_calculated)
    li=calculated+not_calculated
    #if len(li) > 0: print(str(int(100*float(len(calculated))/len(li)))+"% of opponents in database.")
    li=sorted(li,key=lambda x:x[2])
    return(li)

def populate():
    r1=calc('https://www.tapology.com/fightcenter/fighters/nate-diaz')
    map(lambda x:rerate(x),fight_database)
    r2=calc('https://www.tapology.com/fightcenter/fighters/nate-diaz')
    while r1!=r2:
        r1=calc('https://www.tapology.com/fightcenter/fighters/nate-diaz')
        map(lambda x:rerate(x),fight_database)
        r2=calc('https://www.tapology.com/fightcenter/fighters/nate-diaz')
    event_list=open('event_list','r')
    d=eval(event_list.read())
    event_list.close()
    global bankroll
    bankroll=500
    ufctest(.25)

def event_calc():
    event_list=open('event_list','r')
    d=eval(event_list.read())
    event_list.close()
    map(calc_card,d)

def generate_database():
    fd=open('fight_dictionary250','r')
    dictionary=eval(fd.read())
    for i in range(0,len(dictionary)):
       c=fighter(dictionary[i][0][0])
       c.rating_list=map(lambda x: rating(x['number'],x['date']),dictionary[i][1])
       if not(isinstance(map(lambda x:x.date,c.rating_list)[0],list)):
           correct(c)
       c.fight_list=map(lambda x: fight(x['opponent'],x['outcome'],x['date'],x['method'],x['decision'],x['odds']),dictionary[i][2])
       fight_database.insert(0,c)
    fd.close()

def expand(c):
    e=(c.name)
    f=map(vars,c.rating_list)
    g=map(vars,c.fight_list)
    return([[e],f,g])

def add_fighter(c):
    global fight_database
    unique_list=filter(lambda x: x.name!=c.name, fight_database)
    unique_list.insert(0,c)
    fight_database=unique_list

def save_database():
    dictionary=open('fight_dictionary250','w')
    expand_base=map(expand,fight_database)
    dictionary.write(str(expand_base))
    dictionary.close()

def in_database(fight):
    name=fight.opponent[25:]
    name_list=map(lambda x:x.name,fight_database)
    return(name in name_list)

#Further improvement--check to see if the fighters who have the records in the record list are in the database.
#Already done in list_rating
def record_rating(record_list): 
    r=map(lambda x: [fighter_base_rating(x[0]),x[1],x[2]], record_list)
    return(fighter_rating(r))

def fighter_list(query):
    h=get_page(query)
    return(get_fighter_list(h,[]))

def get_fighter_list(html,fighterlist):
   pattern=re.compile('fightCardFighterName left')
   p=pattern.search(html)
   if p:
      q=p.group(0)
      i=html.index(q)
      html=html[i:len(html)]
      pattern=re.compile('fightcenter/fighters/.*\"')
      p2=pattern.search(html)
      q=p2.group(0)
      q=q[0:len(q)-1]
      fighterlist.insert(0,q)
      pattern=re.compile('fightCardFighterName right')
      p=pattern.search(html)
      q=p.group(0)
      i=html.index(q)
      html=html[i:len(html)]
      pattern=re.compile('fightcenter/fighters/.*\"')
      p2=pattern.search(html)
      q=p2.group(0)
      q=q[0:len(q)-1]
      fighterlist.insert(0,q)
      get_fighter_list(html,fighterlist)
   return(fighterlist)

#5 to win 41.55 vs 5 to win 31.20
def expected_value(to_win,cost,win_prob):
    return(to_win*win_prob-cost*(1-win_prob))

def calc_card(query):
    fl=fighter_list(query)
    fl.reverse()
    map(lambda x:calc("https://www.tapology.com/"+x),fl) 


def predict_card(query):
    fl=fighter_list(query)
    fl.reverse()
    fl=map(lambda x:[x,"https://www.tapology.com/"+x],fl) 
    fl=map(lambda x:[x[0],rt(x[1])],fl) 
    fl=pair_up(fl)
    for i in range(0,len(fl)):
        f1 = fl[i][0][1]
        f2 = fl[i][1][1]
        if expected_score(f1,f2) < .5: fl[i].reverse()
        f1 = fl[i][0][1]
        f2 = fl[i][1][1]
        print('\036[1;31;40m \n')
        print(fl[i],expected_score(f1,f2))
        winloss("https://www.tapology.com/"+fl[i][0][0],"https://www.tapology.com/"+fl[i][1][0])
    #return(fl)

def date_card(query,date):
    fl=fighter_list(query)
    fl.reverse()
    fl=map(lambda x:[x,"https://www.tapology.com/"+x],fl) 
    fl=map(lambda x:[x[0],date_rating(x[1],date)],fl) 
    fl=pair_up(fl)
    for i in range(0,len(fl)):
        f1 = fl[i][0][1]
        f2 = fl[i][1][1]
        if expected_score(f1,f2) < .5: fl[i].reverse()
        f1 = fl[i][0][1]
        f2 = fl[i][1][1]
        print(fl[i],expected_score(f1,f2))
        winloss("https://www.tapology.com/"+fl[i][0][0],"https://www.tapology.com/"+fl[i][1][0])

def pair_up(li):
    pairs=[]
    for i in range(0,len(li)):
        if i % 2 == 0: 
            pairs.insert(0,[li[i],li[i+1]])
    pairs.reverse()
    return(pairs)

def deep_card(query):
    fl=fighter_list(query)
    fl.reverse()
    fl=map(lambda x:[x,"https://www.tapology.com/"+x],fl) 
    fl=map(lambda x:[x[0],deep_rating(x[1])],fl) 
    fl=pair_up(fl)
    for i in range(0,len(fl)):
        print(fl[i],expected_score(fl[i][0][1],fl[i][1][1]))
        print('\n')

def outcome(event):
   html=get_page(event)
   pattern=re.compile('eventQuickCardSidebar')
   p=pattern.search(html)
   q=p.group(0)
   i=html.index(q)
   html=html[i:]
   return(outcome_list(html,[]))
   
def outcome_list(html,fl):   
   pattern=re.compile('fightcenter/fighters/.*\"')
   p=pattern.search(html)
   if p: 
      q=p.group(0)
      q=q[:-1]
      i=html.index(q)
      html=html[i+1:]
      if i < 1000:
          fl.insert(0,q)
          outcome_list(html,fl)
   fl.reverse()
   fl=pair_up(fl)
   return(fl)

def fighter_list_date_outcome(query):
    html=get_page(query)
    pattern=re.compile('[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]')
    p=pattern.search(html)
    q=p.group(0)
    q=q.split('.')
    q=shift(q)
    q=map(int,q)
    pattern=re.compile('eventQuickCardSidebar')
    p=pattern.search(html)
    out=p.group(0)
    i=html.index(out)
    html2=html[i:]
    return([q,get_fighter_list(html,[]),outcome_list(html2,[])])

def oddsdate(c,date):
    oddsfight=filter(lambda x:x.date==date,c.fight_list)
    if len(oddsfight)==1: return(oddsfight[0].odds)
    else: return(0)

def shift(seq):
    return [seq[-1]] + seq[:-1]

def event_date(event):
   html=get_page(event)
   pattern=re.compile('[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]')
   p=pattern.search(html)
   q=p.group(0)
   q=q.split('.')
   q=shift(q)
   q=map(int,q)
   return(q)

def max_rating(c):
    return(max(map(lambda x:x.number,c.rating_list)))
def grandmasters():
    gm=filter(lambda x:max_rating(x) > 2500,fight_database)
    for g in gm:
        print(g.name[21:])

def experts():
    gm=filter(lambda x:closest(x,[2020,1,1]) > 2000,fight_database)
    for g in gm:
        print(g.name[21:])

def candidate_masters():
    gm=filter(lambda x:2300 > max_rating(x) >= 2200,fight_database)
    for g in gm:
        print(g.name[21:])

def masters():
    gm=filter(lambda x:2400 > max_rating(x) >= 2300,fight_database)
    for g in gm:
        print(g.name[21:])

def international_masters():
    gm=filter(lambda x:2500 > max_rating(x) >= 2400,fight_database)
    for g in gm:
        print(g.name[21:])

global fight_database
global expand_base
fight_database=[]
expand_base=[]
generate_database()
expand_base=map(expand,fight_database)
