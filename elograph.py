def graph_list(li):
   li=map(lambda x:float(x)/10,li)
   dots=''
   j=0
   for i in li:
       while j < i:
           if j % 4 > 0:
               dots=dots+'*'
           j=j+1
       print int(10*i), dots
       dots=''
       j=0

def pint(i):
    if n < 100:
        return(str(int(10*i))+" ")
    else:
        return(str(int(10*i)))
