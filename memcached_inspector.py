import os 
import argparse
import re 


def memcached_parser(blob): 
    parse_result = []
    print('[*] parsing memcached process memory dump')
    print('index, time, exptime, key, value, flag')
    for i in range(0, len(blob) , 8)  : 
        #if blob[i:i+8] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and blob[i+8:i+16] == b'\x00\x00\x00\x00\x00\x00\x00\x00' :
        if  blob[i+8:i+16] == b'\x00\x00\x00\x00\x00\x00\x00\x00' :
            data_length = blob[i+0x30:i+0x34]
            data_length = int.from_bytes(data_length, byteorder='little')
            if data_length > 2 : 
                if blob[i+0x34:i+0x38] == b'\x00\x00\x04\x00' or  blob[i+0x34:i+0x38] == b'\x01\x00\x03\x00' : 
                    key_length = blob[i+0x39]
                    #key_length = int.from_bytes(key_length, byteorder='little')
                    seperator = blob[i+0x48+key_length:i+0x48+key_length+1]
                    if seperator == b'\x00' :
                        key_data = blob[i+0x48:i+0x48+key_length]
                        value_data = blob[i+0x48+key_length+1:i+0x48+key_length+1+data_length]
                        if value_data[-2:] == b'\x0d\x0a' : # rule can be changed, if memcached use carrige return (\r\n) as input value 
                            # index, time, exptime, key, value, flag 
                            print(int.from_bytes(blob[i+0x40:i+0x44], byteorder='little'),
                            blob[i+0x10:i+0x18], blob[i+0x18:i+0x20] ,  key_data.decode(), value_data.decode(), blob[i+0x34:i+0x38])
                            parse_result.append([int.from_bytes(blob[i+0x40:i+0x44], byteorder='little'),
                            blob[i+0x10:i+0x18], blob[i+0x18:i+0x20] ,  key_data.decode(), value_data.decode(), blob[i+0x34:i+0x38]])

    return parse_result
                     
def processing(memcached_instance) : 
    print('\n\n[*] Report if something special....\n\n')
    for i in memcached_instance : 
        if i[-1] == b'\x00\x00\x04\x00' : 
            print('[*] %s' , i , ' is expired key-value, not shown in running memcahced process (deleted or modified)' )

    index_delta =  [memcached_instance[i][0] - memcached_instance[i+1][0]  for i in range(0,len(memcached_instance)-1)]
    for i, j  in enumerate(index_delta) :
        if j < 0 :
            print('[*] %s' , memcached_instance[i] , ' is modified key-value, cannot found original data' )

    # modified rule 탐지할때 index delta 값이 아닌 index 값 기준으로 맨 뒤에서 부터 0 ,1,2,3,4,5 역순으로 해서 차이 있는지 여부를 봐도 될듯? 
    # => but 큰 데이터베이스에서는 modifiying이 비일비재 할 것이므로 큰 의미는 없을 지도?

"""
Rule, all offset in rule are relative offset
read 16 byte until the end, last eight bytes all 0x00, if not, move pointer 8 bytes
if true, move 0x30 and read 4 byte to little endian that 4 byte integer must bigger than 2, as 'data length'
        if true, move to 0x34 and read 4bytes, find out the flag is expired(00 00 04 00)or live(01 00 03 00)
            if true, move 0x39 and read 1byte as 'key length' and moved again to 0x48 
                if true, read 'key length'+1 bytes above and translate as 'key' value and last byte must 0x00 as seperator
                    if true, read 'data length' bytes and last 2bytes must (0D 0A => \r\n => carrige return?)
                        return recovered instance
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='-f for filepath')
    parser.add_argument('-f','--filepath', help='filepath', required=True)
    args = parser.parse_args()
    fp =args.filepath
    
    print("Filename %s",fp)
    f = open(fp,'rb')
    mem_binary = f.read()
    parsed = memcached_parser(mem_binary)
    if len(parsed) > 0 : 
        processing(parsed)
    else : 
        print('[*] Error occured')
    