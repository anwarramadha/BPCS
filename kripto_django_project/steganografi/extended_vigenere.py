extended_ascii = [chr(i) for i in xrange(256)]

def encrypt(plaintext, key):
	key_length = len(key)
	key_char_itt = 0
	cipher_text = ''

	for c in plaintext:

		if c in extended_ascii:
			if key_char_itt == key_length:
				key_char_itt = 0

			plain_index = extended_ascii.index(c)
			key_index = extended_ascii.index(key[key_char_itt])

			key_char_itt += 1

			chip_index = (plain_index + key_index) % len(extended_ascii)

			cipher_text += extended_ascii[chip_index]
		else:
			cipher_text += c
	return cipher_text

def decrypt(ciphertext, key):
	key_length = len(key)
	key_char_itt = 0
	plaintext = ''

	for c in ciphertext:
		if c in extended_ascii:
			if key_char_itt == key_length:
				key_char_itt = 0

			chip_index = extended_ascii.index(c)
			key_index = extended_ascii.index(key[key_char_itt])

			key_char_itt += 1

			plain_index = (chip_index - key_index) % len(extended_ascii)
			
			plaintext += extended_ascii[plain_index]
		else:
			plaintext += c

	return plaintext
