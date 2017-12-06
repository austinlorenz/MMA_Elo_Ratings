K=250

def actual_base_score(w,l,d):
    return(w + .5*d) 

def expected_base_score(w,l,d):
    return(.5*(w+l+d))

def expected_score(rA,rB): 
    return(1 / (1 + (10**((rB-rA)/float(400)))))

def new_rating(rA,rBscore): 
    #global J
    #K=90
    #K=3*(J-len(rBscore))
    return(rA + K*(rBscore[1]-expected_score(rA,rBscore[0])))

def fighter_base_rating(li): 
    w = li[0] 
    l = li[1] 
    d = li[2] 
    #K=90
    return(1000 + K*(actual_base_score(w,l,d)-expected_base_score(w,l,d)))

#score_list will have form [[1120,1,date],[1050,0,date],...] */
def fighter_rating(score_list): 
    #score_list=date_filter(score_list,2000)
    score_list=sorted(score_list,key=lambda x:x[2])
    score_list.insert(0,1000)
    return(reduce(new_rating,score_list)) 
