import time

def esync():
                 skibidi = int(time.time() * 1000)
                 return str(skibidi - (skibidi) % 21600)
            
print(esync())

