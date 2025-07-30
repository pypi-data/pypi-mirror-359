def hs(*args, sep=' ', end='\n'):
    """
    hs(*args, sep=' ', end='\\n') funktioniert wie print, aber unter deinem Kürzel.
    """
    print(*args, sep=sep, end=end)

def navex(*args, sep=' ', end='\n'):
    """
    navex(*args, sep=' ', end='\\n'):
    - Wenn keine args übergeben werden, wird "Navex ist so ein süsser" ausgegeben.
    - Sonst funktioniert es wie print().
    """
    if args:
        print(*args, sep=sep, end=end)
    else:
        print("Navex ist so ein süsser", end=end)
