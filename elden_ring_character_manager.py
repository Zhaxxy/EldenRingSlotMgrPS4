import _elden_ring_save_constants as ersc
from io import BytesIO
import struct
from typing import NamedTuple

class CharacterName(NamedTuple):
    name: str
    slot_number: int
    in_use: bool

def _update_character_slot(save_file: BytesIO, slot_number: int, status: bool, output_file: BytesIO = None): 
    output_file = save_file if output_file is None else output_file
    
    real_index = slot_number - 1

    if real_index < 0:
        raise IndexError('list assignment index out of range')

    save_file.seek(0)
    output_file.seek(0)
    
    save_file.seek(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET)
    
    slots_in_use_arrays = list(struct.unpack(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING, save_file.read(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_LENGTH)))
    slots_in_use_arrays[real_index] = status

    save_file.seek(0)
    output_file.seek(0)

    output_file.seek(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET)

    output_file.write(struct.pack(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING, *slots_in_use_arrays))
    
    output_file.seek(0)

def resurrect_character_slot(slot_number: int,save_file: BytesIO,output_file: BytesIO = None):
    _update_character_slot(save_file, slot_number, True, output_file)

def delete_character_slot(slot_number: int, save_file: BytesIO,output_file: BytesIO = None):
    _update_character_slot(save_file, slot_number, False, output_file)


def copy_character_slot(slot_number_to_copy_from: int ,save_file_to_copy_from: BytesIO ,slot_number_to_copy_to: int, output_save_to_copy_to: BytesIO = None, resurrect_slot: bool = False):
    output_save_to_copy_to = save_file_to_copy_from if output_save_to_copy_to is None else output_save_to_copy_to
    
    real_slot_number_to_copy_from = slot_number_to_copy_from - 1
    real_number_to_copy_to = slot_number_to_copy_to - 1

    if real_slot_number_to_copy_from < 0 or real_number_to_copy_to < 0:
        raise IndexError('list assignment index out of range')

    save_file_to_copy_from.seek(0)
    output_save_to_copy_to.seek(0)

    # get the data blocks
    save_file_to_copy_from.seek(ersc.CHARACTER_DATA_SECTIONS_AND_OFFSETS[real_slot_number_to_copy_from].data_section_offset)
    data_section_copy = save_file_to_copy_from.read(ersc.CHARACTER_DATA_SECTION_LENGTH)

    save_file_to_copy_from.seek(0)

    save_file_to_copy_from.seek(ersc.CHARACTER_DATA_SECTIONS_AND_OFFSETS[real_slot_number_to_copy_from].load_screen_offset)
    load_screen_copy = save_file_to_copy_from.read(ersc.LOAD_SCREEN_SECTION_LENGTH)
    save_file_to_copy_from.seek(0)

    # get the boolean if the slot is in use or not, we dont want to use the one in the other save, we want this one
    save_file_to_copy_from.seek(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET)
    is_in_use = struct.unpack(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING, save_file_to_copy_from.read(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_LENGTH))[real_slot_number_to_copy_from]
    save_file_to_copy_from.seek(0)

    #get the array from the other save
    output_save_to_copy_to.seek(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET)

    slots_in_use_arrays = list(struct.unpack(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING, output_save_to_copy_to.read(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_LENGTH)))
    
    slots_in_use_arrays[real_number_to_copy_to] = True if resurrect_slot else is_in_use
    # finnaly, input the data into the output save file, to the wanted slot
    output_save_to_copy_to.seek(0)
    output_save_to_copy_to.seek(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET)
    output_save_to_copy_to.write(struct.pack(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING, *slots_in_use_arrays))
    output_save_to_copy_to.seek(0)

    output_save_to_copy_to.seek(ersc.CHARACTER_DATA_SECTIONS_AND_OFFSETS[real_number_to_copy_to].data_section_offset)
    output_save_to_copy_to.write(data_section_copy)
    output_save_to_copy_to.seek(0)

    output_save_to_copy_to.seek(ersc.CHARACTER_DATA_SECTIONS_AND_OFFSETS[real_number_to_copy_to].load_screen_offset)
    output_save_to_copy_to.write(load_screen_copy)
    output_save_to_copy_to.seek(0)


def is_character_slot_in_use(slot_number: int, save_file: BytesIO) -> bool:
    real_index = slot_number - 1

    if real_index < 0:
        raise IndexError('list assignment index out of range')

    save_file.seek(0)

    save_file.seek(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET)
    result = struct.unpack(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING, save_file.read(ersc.SLOTS_IN_USE_BOOLEAN_ARRAY_LENGTH))[real_index]
    save_file.seek(0)
    return result

def get_character_slot_name(slot_number: int, save_file: BytesIO) -> CharacterName:
    real_index = slot_number - 1

    if real_index < 0:
        raise IndexError('list assignment index out of range')

    save_file.seek(0)
    save_file.seek(ersc.CHARACTER_DATA_SECTIONS_AND_OFFSETS[real_index].load_screen_offset)
    
    name = save_file.read(ersc.CHARACTER_NAME_LENGTH).replace(b'\x00',b'').decode('utf-8')
    save_file.seek(0)

    return CharacterName(name,slot_number,is_character_slot_in_use(slot_number,save_file))

def is_valid_save(save_file: BytesIO) -> bool:
    save_file.seek(0)
    save_file.seek(0,2)
    save_size = save_file.tell()
    save_file.seek(0)
    magic_header = save_file.read(4)
    save_file.seek(0)
    return magic_header == ersc.SAVE_FILE_MAGIC_HEADER and save_size == ersc.SAVE_FILE_SIZE


class InvalidEldenRingSavePS4(Exception):
    """Error to rasie if a bad save"""


def check_save(save_file: BytesIO) -> None:
    if not is_valid_save(save_file):
        raise InvalidEldenRingSavePS4('Invalid PS4 save file, is it decrypted?')

def main():
    with open('memory.dat','rb+') as ff, open('MODDEDmemory.dat','rb+') as modded_f:
        
        check_save(ff);check_save(modded_f)
        
        copy_character_slot(1,modded_f,3,ff)

        delete_character_slot(8,ff)
        
        for x in range(1,11):
            print(get_character_slot_name(x,ff))

if __name__ == '__main__':
    main()
