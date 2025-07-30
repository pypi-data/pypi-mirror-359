# d - ალფავიტში სიმბოლოების რაოდენობა
d = 256  # ჩვეულებრივ ASCII სიმბოლოებისთვის

# ნიმუშის (pattern) და ტექსტის (text) შერჩევა
def search(pattern, text, prime_modulus):
    pattern_length= len(pattern)  # ნიმუშის სიგრძე
    text_length = len(text)  # ტექსტის სიგრძე
    hash_pattern = 0    # ნიმუშის ჰეშ-მნიშვნელობა
    hash_text = 0    # ტექსტის ქვეწინადადების ჰეშ-მნიშვნელობა
    h = 1  # წინასწარი მნიშვნელობა, რომელიც გამოიყენება ჰეშის განახლებისთვის

    # ჰეშ-ის განახლების დაწყება
    for i in range(pattern_length-1):
        h = (h*d) % prime_modulus

    # ნიმუშის და პირველი ქვეწინადადების ჰეშ-ფუნქციების გამოთვლა
    for i in range(pattern_length):
        hash_pattern = (d*hash_pattern + ord(pattern[i])) % prime_modulus
        hash_text = (d*hash_text + ord(text[i])) % prime_modulus

    # ნიმუშის გადაადგილება ტექსტში
    for i in range(text_length-pattern_length+1):
        # თუ ჰეშ-მნიშვნელობები ემთხვევა, შეამოწმე სიმბოლოები
        if hash_pattern == hash_text:
            for j in range(pattern_length):
                if text[i+j] != pattern[j]:
                    break
            else:
                print("Pattern found at index " + str(i))

        # შემდეგი ქვეწინადადების ჰეშ-მნიშვნელობის გამოთვლა
        if i < text_length-pattern_length:
            hash_text = (d*(hash_text - ord(text[i])*h) + ord(text[i+pattern_length])) % prime_modulus
            if hash_text < 0:
                hash_text = hash_text + prime_modulus

# Driver Code
if __name__ == '__main__':
    text = "GEEKS FOR GEEKS"
    pattern = "GEEK"

    prime_modulus = 101
 
    # ფუნქციის გამოძახება
    search(pattern, text, prime_modulus)
