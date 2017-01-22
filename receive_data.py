#---------------------------------------
# received uart data from audio in
#
# aixi.wang@hotmail.com
#---------------------------------------

import pyaudio
import wave
import sys
import time

THRESHOLD1 = 65536/4

header_detect_cnt1 = 0
header_detect_cnt2 = 0

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

IDEL_DURATION = RATE

last_d = 0
bit_array = []
bit_state_machine_status = 0

last_i = None
last_j = None
    
#-------------------------
# feature_energy
#-------------------------
def feature_energy(raw_data,n):
    e = 0
    i = 0;
    high_b = 0
    for i in range(0,n):
        d = ord(raw_data[i*2]) + ord(raw_data[i*2+1])*256
        if d >= 65536/2:
            d2 = d - 65536
        else:
            d2 = d
        #print 'n:',i,'d2:',d2
        e += d2*d2
    return e/n   

#---------------------
# bit_remove_balance
#---------------------  
def bit_remove_balance(arr):
    if len(arr) % 2 == 1 and arr[-1] == 1 and arr[-2] == 0:
        return arr[:-1]
    else:
        return arr
        
#-------------------------
# bitarray_to_str
#-------------------------
def bitarray_to_str(arr):
    i = len(arr);

    if (i % 8) != 0:
        #print 'invalid bit received'
        return ''

    i = i/8
        
    s = ''
    for i in range(0,i):
        d = 128*arr[i*8] + 64*arr[i*8+1] + 32*arr[i*8+2] + 16*arr[i*8+3]
        d += 8*arr[i*8+4] + 4*arr[i*8+5] + 2*arr[i*8+6] + 1*arr[i*8+7]
        s += chr(d)
    
    return s

#-------------------------
# validate_and_retrieve_raw
#-------------------------    
def validate_and_retrieve_raw(s):
    retcode = 0
    if len(s) < 4:
        return -1, ''
    
    if s[0] != '\x55':
        return -2, ''
    
    if ord(s[1]) != len(s)-3:
        return -3, ''
        
    checksum = 0
    for i in range(2,len(s)-1):
        #print 'i:',i
        checksum += ord(s[i])
    checksum %= 256
    
    if ord(s[-1]) != checksum:
        return -4,''
    
    return 0, s[2:-1]
#-------------------------
# decode_uart_data
#-------------------------    
def do_idle():
    global header_detect_cnt1
    global header_detect_cnt2
    
    global last_d
    global bit_state_machine_status
    global bit_array
    
    global last_i
    global last_j

    last_i = None
    last_j = None                    
    
    last_d = 0
    
    bit_state_machine_status = 0
    if len(bit_array) > 0:
        #print 'bit_array :',len(bit_array),',',bit_array
        bit_array2 = bit_remove_balance(bit_array)
        #print 'bit_array2:',len(bit_array2),',',bit_array2
        s2 = bitarray_to_str(bit_array2)
        retcode, s3 = validate_and_retrieve_raw(s2)
        if retcode == 0:
            print'received str(hex):',s3.encode('hex')
            print'received str:',s3
            
        else:
            print'received str(hex):',s2.encode('hex')
            print'received str:',s2
        
            print 'retcode:',retcode,', package integration checking fail'
            
        bit_array = []    
#-------------------------
# decode_uart_data
#-------------------------
def decode_uart_data(raw_data,n):
    global header_detect_cnt1
    global header_detect_cnt2
    
    global last_d
    global bit_state_machine_status
    global bit_array
    
    global last_i
    global last_j
    
    e = 0
    i = 0;
    high_b = 0

    for i in range(0,n):
        d = ord(raw_data[i*2]) + ord(raw_data[i*2+1])*256
        if d >= 65536/2:
            d2 = d - 65536
        else:
            d2 = d
        
        if last_d < THRESHOLD1:
            header_detect_cnt1 += 1
            if header_detect_cnt1 > IDEL_DURATION:
                #print '=== idle detected ===='
                do_idle()
                header_detect_cnt1 = 0                
                
        else:
            header_detect_cnt1 = 0

        if last_d > THRESHOLD1:
            header_detect_cnt2 += 1
            if header_detect_cnt1 > IDEL_DURATION:
                #print '=== idle detected ===='
                do_idle()
                header_detect_cnt2 = 0
        else:
            header_detect_cnt2 = 0

        #print 'n:',i,'d2:',d2
        if last_d < THRESHOLD1 and d2 >= THRESHOLD1:
            #print '>',i,'\r\n'
            last_i = i


        elif last_d > THRESHOLD1 and d2 <= THRESHOLD1:
            #print '<',i,'\r\n'
            bit_state_machine_status += 1            
            last_j = i
            if last_i != None:
                if last_j > last_i:
                    distance = last_j - last_i
                else:
                    distance = last_j + CHUNK - last_i

                #print 'distance2:',distance
                if distance >=22 and distance <= 23:
                    #print '0'

                    bit_array.append(0)
                    
                elif distance >=7 and distance <= 9:
                    #print '1'
                    bit_array.append(1)
                else:
                    #print 'distance:',distance
                    pass
        last_d = d2

#------------------------------------------
# main
#------------------------------------------
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                output = False,
                input_device_index = 2,                
                frames_per_buffer = CHUNK)

print "listing..."

while True:
    try:
        data = stream.read(CHUNK)
        
        #d = feature_energy(data,CHUNK)
        #print 'data:', str(d),'\r\n'
        decode_uart_data(data,CHUNK)
    except Exception as e:       
        print 'audio exception, retry', str(e)
        time.sleep(1)





