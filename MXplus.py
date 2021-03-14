import sys


def main (sc1, t1, sc2, t2): 
    print(sc1, t1, sc2, t2)
    m=(t2-t1)/(sc2-sc1)
    b=t1-(m*sc1)
    return (m, b)


if __name__ == '__main__': 
    #Error checking

    args= [int(a) for a in sys.argv[1:5]]

    m,b=    main(*args)
    print(m, b) 