import random
import os
import sys
from encryption.Rabin import rabinMiller
from encryption.Math import cryptomath

def main():
    print('Making encrypted key files...')
    makeKeyFiles('IncfCrypto', 1024)
    print('Key files made.')

def generateKey(keySize):
    print('Generating p prime...')
    p = rabinMiller.generateLargePrime(keySize)
    print('Generating q prime...')
    q = rabinMiller.generateLargePrime(keySize)
    n = p * q

    print('Generating e that is reletively prime to (p-1)*(q-1)...')
    while True:
        e = random.randint(2 ** (keySize - 1), 2 ** (keySize))
        if cryptomath.gcd(e, (p - 1) * (q - 1)) == 1:
            break

        print('Calculating d that is mod inverse of e...')
        d = cryptomath.findModInverse(e, (p - 1) * (q - 1))

        publickey = (n, e)
        privatekey = (n, d)

        print('Public key:', publickey)
        print('private key:', privatekey)

def makeKeyFiles(name, keySize):
    if os.path.exists('%s_pubkey.txt' % (name)) or os.path.exists('%s_privkey.txt' % (name)):
        sys.exit('WARNING: The file %s_pubkey.txt or %s_privkey.txt already exist! use a different name or delete these files and re-run this program.' % (name, name))

        publickey, privatekey = generateKey(keySize)

        print()
        print('The public key is a %s and a %s digit number.' % len(str(publickey[0]))), len(str(publickey[1]))
        print('Writing private key to file %s_privkey' % (name))
        fo = open('%s_privkey.txt' % (name), 'w')
        fo.write('%s,%s,%s' % (keySize, publickey[0], publickey[1]))
        fo.close()

        print()
        print('The private key is a %s and a %s digit number.' %
              (len(str(publickey[0])), len(str(publickey[1]))))
        print('Writing private key to file %s_privatekey.txt...' % (name))
        fo = open('%s_privkey.txt' % (name), 'w')
        fo.write('%s,%s,%s' % (keySize, privatekey[0], privatekey[1]))
        fo.close()

if __name__ == '__main__':
    main()

