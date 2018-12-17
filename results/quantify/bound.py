INPUT_WIJK = "bound.txt"

with open(f"{INPUT_WIJK}", 'r') as f:

    for wijk in f:

        name = wijk.strip()
        wijk = f.readline()
        lower = wijk.split()
        lower = float(lower[1])

        wijk = f.readline()
        upper = wijk.split()
        upper = float(upper[1])

        wijk = f.readline()
        our = wijk.split()
        our = float(our[1])

        wijk = f.readline()
        upper -= lower
        our -= lower

        kwant = our/upper * 100

        print(f"wijk{name}: {kwant}%")
