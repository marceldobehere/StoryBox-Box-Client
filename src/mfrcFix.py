from textwrap import wrap

KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

BLOCKS = []
KEY_BLOCKS = []
for i in range(1, 16):
    print(i*4)
    temp = i*4
    BLOCKS.append(list(range(temp, temp + 3)))
    KEY_BLOCKS.append(temp + 3)


print("BLOCKS: ", BLOCKS)

print("KEY BLOCKS:", KEY_BLOCKS)


def write_blocks(reader, text, blockCount):
    split = wrap(text, 16*3)
    if blockCount > 15:
        print("ERR: BLOCK COUNT TOO HIGH!!!")
        blockCount = 15

    while len(split) < blockCount:
        split.append("")
    # print("SPLIT: ", split)
    if len(split) > blockCount:
        print("ERR: TOO FEW BLOCKS FOR TEXT DATA TO WRITE!!!")

    for i in range(blockCount):
        print("> writing Blocks ", BLOCKS[i], " with ", split[i])
        write_block(reader, split[i], BLOCKS[i], KEY_BLOCKS[i])

def read_blocks(reader, blockCount):
    if blockCount > 15:
        print("ERR: BLOCK COUNT TOO HIGH!!!")
        blockCount = 15
    res = ""
    out_id = None
    for i in range(blockCount):
        out_id, text = read_block(reader, BLOCKS[i], KEY_BLOCKS[i])
        res += text
    return out_id, res

# write_blocks(None, "1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF", 4)
# print(read_blocks(None, 4))


def write_block(reader, text, blocks, keyBlock):
    id, text_in = internal_write_block(reader, text, blocks, keyBlock)
    while not id:
        id, text_in = internal_write_block(reader, text, blocks, keyBlock)
    return id, text_in

def internal_write_block(reader, text, blocks, keyBlock):
    (status, TagType) = reader.READER.MFRC522_Request(reader.READER.PICC_REQIDL)
    if status != reader.READER.MI_OK:
        return None, None
    (status, uid) = reader.READER.MFRC522_Anticoll()
    if status != reader.READER.MI_OK:
        return None, None
    id = reader.uid_to_num(uid)
    reader.READER.MFRC522_SelectTag(uid)
    status = reader.READER.MFRC522_Auth(reader.READER.PICC_AUTHENT1A, keyBlock, reader.KEY, uid)
    reader.READER.MFRC522_Read(keyBlock)
    if status == reader.READER.MI_OK:
        data = bytearray()
        data.extend(bytearray(text.ljust(len(blocks) * 16).encode('ascii')))
        i = 0
        for block_num in blocks:
            reader.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
            i += 1
    reader.READER.MFRC522_StopCrypto1()
    return id, text[0:(len(blocks) * 16)]


def read_block(reader, blocks, keyBlock):
    id, text_in = read_no_block(reader, blocks, keyBlock)
    while not id:
        id, text_in = read_no_block(reader, blocks, keyBlock)
    return id, text_in


def read_no_block(reader, blocks, keyBlock):
    (status, TagType) = reader.READER.MFRC522_Request(reader.READER.PICC_REQIDL)
    if status != reader.READER.MI_OK:
        return None, None
    (status, uid) = reader.READER.MFRC522_Anticoll()
    if status != reader.READER.MI_OK:
        return None, None
    id = reader.uid_to_num(uid)
    reader.READER.MFRC522_SelectTag(uid)
    status = reader.READER.MFRC522_Auth(reader.READER.PICC_AUTHENT1A, keyBlock, reader.KEY, uid)
    data = []
    text_read = ''
    if status == reader.READER.MI_OK:
        for block_num in blocks:
            block = reader.READER.MFRC522_Read(block_num) 
            if block:
                data += block
        if data:
            text_read = ''.join(chr(i) for i in data)
    reader.READER.MFRC522_StopCrypto1()
    return id, text_read