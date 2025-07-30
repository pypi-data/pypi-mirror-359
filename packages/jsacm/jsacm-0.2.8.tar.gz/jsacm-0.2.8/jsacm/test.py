import jsacm
def asymetrical_encryption(*argv): # can take in binary input
    bininp = []
    import random
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            bininp = str(arg)
    if check != True:
        bininp = input("Enter first binary number:")
    pubencry = []
    privencry = []
    pubxor = []
    privxor = []
    result = ""
    for i in range(len(bininp)):
        x = random.randint(0,1)
        pubxor += str(x)
    for i in range(len(bininp)):
        x = random.randint(0,1)
        privxor += str(x)
    pos = 0
    for i in bininp:
        if privxor[pos] == "1":
            privencry.append("1")
        elif privxor[pos] == "0":
            privencry.append(str(i))
        pos += 1
    pos1 = 0
    for i in privencry:
        if pubxor[pos1] == "1":
            pubencry.append("1")
        elif pubxor[pos1] == "0":
            pubencry.append(str(i))
        pos1 += 1
    result = "".join(pubencry)
    pubxor = int(''.join(map(str, pubxor)))
    privxor = int(''.join(map(str, privxor)))
    answer = (f"Public key: {pubxor} Private key: {privxor} Original: {bininp} Encrypted: {result}")
    if check == True:
        return answer
    else:
        print(answer)
asymetrical_encryption()