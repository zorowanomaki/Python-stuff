def DtoB(dec, bit_len): #Decimal to Binary
    binary = bin(dec) #A function found online that converts decimals into binary (has an annoying "0b" at the start).
    binary = binary[2:] #The [2:] is there to skip the "0b" at the start.
    if len(binary) < bit_len: #Checks to see if we have enough 0 (empty spaces) in our output.
        binary = binary.zfill(bit_len) #If not, fill in 0 (that's what .zfill does).
    return binary
def ComTo2(binary, bit_len): #A function that puts to use the "completion to 2" method.
    inv = ''.join('1' if bit == '0' else '0' for bit in binary) # Inverts all bits in binary and then puts it in a list called "inv" (inverted).
    inv_dec = int(inv, 2) + 1 #Converts the inverted binary (inv) back into decimal, and adds one (becasue we are using "completion to 2").
    return_value = DtoB(inv_dec, bit_len) #Converts inv_dec into binary after adding the 1, and puts it into a new place
    if len(return_value) > bit_len: return_value = ''.join('0' for i in range(0, bit_len)) #mostly to prevent 0 from gliching out.
    return return_value


# Main
decimal = input("Enter decimal positive number: ")
while decimal.isnumeric() == False: decimal = input("My guy, i said a positive number (or 0). Please enter a decimal number: ") #checks if the user's input is a number or not, if its not it makes the user give a new input.
bit_len = input("How much bits does the number need?: ")
while bit_len.isnumeric() == False or int(bit_len) <= 0: bit_len = input("Dude, amount has to be a positive number. How much bits does the number need?: ") #checks if the user's input is a number or not, if its not it makes the user give a new input.
binary = DtoB(int(decimal), int(bit_len)) #Calls the function that we made earlier.
print ("Positive in binary: ", binary)
print ("Negetive in binary: ", ComTo2(binary, int(bit_len)))