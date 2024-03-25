from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import cv2
import hashlib
import os

# Function to capture eyes and generate encryption key
def capture_eyes():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Display the frame
        cv2.imshow('Capture Eyes', frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

    # Process the captured image to generate encryption key
    key = hashlib.sha256(frame.tobytes()).digest()
    return key

# Function to encrypt a file using AES encryption
def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        plaintext = file.read()

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.iv + cipher.encrypt(pad(plaintext, AES.block_size))

    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as file:
        file.write(ciphertext)

    return encrypted_file_path

# Function to decrypt a file using AES decryption
def decrypt_file(encrypted_file_path, key):
    with open(encrypted_file_path, 'rb') as file:
        ciphertext = file.read()

    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        plaintext = unpad(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
    except ValueError as e:
        print("Error: Incorrect decryption key or padding.")
        return None

    decrypted_file_path = os.path.splitext(encrypted_file_path)[0]  # Remove '.enc' extension
    with open(decrypted_file_path, 'wb') as file:
        file.write(plaintext)

    return decrypted_file_path

# Function to calculate the Hamming distance between two keys
def hamming_distance(key1, key2):
    distance = sum(b1 != b2 for b1, b2 in zip(key1, key2))
    return distance

if __name__ == "__main__":
    print("Option 1: Encrypt File")
    print("Option 2: Decrypt File")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        print("Please position your face to capture your eyes.")
        print("Press 'q' to capture.")
        key = capture_eyes()

        file_path = input("Enter the path of the file to encrypt: ")
        encrypted_file_path = encrypt_file(file_path, key)
        print("File encrypted successfully:", encrypted_file_path)

    elif choice == '2':
        encrypted_file_path = input("Enter the path of the encrypted file: ")

        print("Please position your face to capture your eyes.")
        print("Press 'q' to capture.")
        key = capture_eyes()

        # Check if the Hamming distance between keys is within 50% tolerance
        tolerance = len(key) // 2
        key_from_image = hashlib.sha256(key).digest()
        key_from_file = hashlib.sha256(key).digest()
        distance = hamming_distance(key_from_image, key_from_file)
        if distance <= tolerance:
            print("Keys match with a Hamming distance of:", distance)
            decrypted_file_path = decrypt_file(encrypted_file_path, key)
            if decrypted_file_path:
                print("File decrypted successfully:", decrypted_file_path)
        else:
            print("Keys do not match. Please ensure you are using the same eyes for decryption.")

    else:
        print("Invalid choice. Please enter '1' or '2'.")
