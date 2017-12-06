def break_even(x): 
    if x < 0: 
        return(minus_convert(x)) 
    else: 
        return(plus_convert(x))
def minus_convert(x):
    return(-float(x) / (-x+100))

def plus_convert(x): 
    return(float(100) / (x+100))

def to_decimal(quote):
    if quote < 0:
        return(100./abs(quote)+1)
    else:
        return(float(quote)/100+1)

def juice(dog,fave):
    return(100*((1. / (break_even(dog)+break_even(fave)))-1))

def edge(odds,win_rate):
    return(100*(to_decimal(odds)*win_rate-1))

def kelly(odds,win_prob,bankroll):
    odds=to_decimal(odds)
    loss_prob=1-win_prob
    k=float(((odds-1)*win_prob)-loss_prob)/(odds-1)
    print(k)
    return(k*bankroll)
