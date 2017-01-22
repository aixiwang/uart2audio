#---------------------------------------
# send data to audio jack from serial ttl
# hardware    ttl tx  <-> audio jack l,r
#             ttl gnd <-> audio jack gnd
#
# aixi.wang@hotmail.com
#---------------------------------------

import serial
import time

s_handle = serial.Serial(port='COM8',baudrate=9600,timeout = 0.1)
print 'start to send...'

#---------------------
# create_bit0
#---------------------  
def create_bit0():
    return '\xf0'

#---------------------
# create_bit1
#---------------------  
def create_bit1():
    return '\xcc'

#---------------------
# char_to_bitarray
#---------------------  
def char_to_bitarray(c):
    bit_arr = []
    d = ord(c)
    bit_arr.append(d / 128)
    bit_arr.append((d%128) / 64)
    bit_arr.append((d%64) / 32)
    bit_arr.append((d%32) / 16)
    bit_arr.append((d%16) / 8)
    bit_arr.append((d%8) / 4)
    bit_arr.append((d%4) / 2)
    bit_arr.append((d%2) / 1)
    return bit_arr
    
#---------------------
# bit_balance2
#---------------------  
def bit_balance2(arr):
    n = len(arr)
    j1 = 0
    j2 = 0
    arr2 = []
    for i in range(0,n):
        if arr[i] == 1:
            j2 = 0
            j1 += 1
            if j1 > 5:
                arr2.append(1)
                arr2.append(0)
                j1 = 0
            else:
                arr2.append(1)
            
        else:
            j1 = 0
            j2 += 1
            if j2 > 5:
                arr2.append(0)
                arr2.append(1)
                j2 = 0
            else:
                arr2.append(0)

    return arr2

#---------------------
# bit_balance
#---------------------  
def bit_balance(arr):
    n = len(arr)
    j1 = 0
    j2 = 0
    arr2 = arr
    if arr2[-1] == 0:
        arr2.append(1)
    
    return arr2    
#---------------------
# create_byte
#---------------------   
def create_byte(c):
    s = ''
    if ord(c) & 0x80:
        s += create_bit1()
    else:
        s += create_bit0()
    
    if ord(c) & 0x40:
        s += create_bit1()
    else:
        s += create_bit0()

    if ord(c) & 0x20:
        s += create_bit1()
    else:
        s += create_bit0()

    if ord(c) & 0x10:
        s += create_bit1()
    else:
        s += create_bit0()

    if ord(c) & 0x08:
        s += create_bit1()
    else:
        s += create_bit0()
    if ord(c) & 0x04:
        s += create_bit1()
    else:
        s += create_bit0()
    if ord(c) & 0x02:
        s += create_bit1()
    else:
        s += create_bit0()
        
    if ord(c) & 0x01:
        s += create_bit1()
    else:
        s += create_bit0()
    return s

#---------------------
# send_str_pre
#---------------------    
def send_str_pre(s):   
    checksum = 0
    for c in s:
        checksum += ord(c)
    checksum = checksum % 256
    
    s2 = '\x55' + chr(len(s)) + s + chr(checksum)
    
    print 's2(hex):',s2.encode('hex')
    
    bit_array = []
    for c in s2:
        bit_array += char_to_bitarray(c)
        
    #print 'bit_array:',len(bit_array),bit_array
    bit_array2 = bit_balance(bit_array)
    #bit_array2 = bit_array
    #print 'bit_array2:',len(bit_array2),bit_array2
    temp_s = ''
    for b in bit_array2:
        if b == 1:
            temp_s += create_bit1()
        else:
            temp_s += create_bit0()
    
    return temp_s    
        
#---------------------
# main
#---------------------          
while(1):
    try:
        s = raw_input(':>')
        if len(s) > 0:
            s2 = send_str_pre(s)
            #print 's2:',s2.encode('hex')
            s_handle.write(s2)
            s_handle.flush()
        time.sleep(1)
    except:
        pass
    