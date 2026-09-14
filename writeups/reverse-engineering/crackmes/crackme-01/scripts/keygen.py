# 1. Get the user's input name
name = input("Enter the Name: ")

# 2. Get the length of the string and store it in a distinct variable
name_length = len(name)

# 3. Perform the addition (0xCA is 202 in decimal)
name_length += 0xCA

# 4. Perform the bitwise XOR operation with the corrected hex prefix
name_length ^= 0x3D8D40F

# 5. Print the final calculated serial key
print("Your Serial Key (Decimal):", name_length)
print("Your Serial Key (Hex):", hex(name_length).upper())

input("")