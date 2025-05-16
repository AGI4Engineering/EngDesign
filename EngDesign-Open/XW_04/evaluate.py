import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from solution import golden_read,golden_write,golden_create
from solution import SuperBlock, FileSystemImage, Inode, DirEntry, Optional, List, Dict


def evaluate_llm_response(llm_response):
    print(llm_response)
    confidence = 100
    sb = SuperBlock(block_size=512, total_blocks=16, inode_count=16,
    free_block_bitmap=[True]*16)
    fs = FileSystemImage(sb)
    root = fs.create_inode(is_dir=True)  # ino = 1
    
    # get the function from the LLM response
    # Create namespace with required classes
    namespace = {
        'FileSystemImage': FileSystemImage,
        'SuperBlock': SuperBlock,
        'Inode': Inode,
        'DirEntry': DirEntry,
        'Optional': Optional,
        'List': List,
        'Dict': Dict
    }

    exec(llm_response.config.delete, namespace)
    
    delete = namespace['delete']

    details = {}
    score = 0

    print("Testing file system operations...")
    
    # 1) delete a valid file
    try:
        fs2 = golden_create(fs, '/foo.txt', is_dir=False)
        fs3 = delete(fs2, '/foo.txt')
        try:
            golden_read(fs3, '/foo.txt', 0, 1)
            details['delete'] = False
        except FileNotFoundError:
            details['delete'] = True
            score += 20
    except Exception as e:
        details['delete'] = False
    # 2) delete valid directories
    try:
        sb2 = SuperBlock(block_size=512, total_blocks=16, inode_count=16,
                         free_block_bitmap=[True]*16)
        fs2 = FileSystemImage(sb2)
        fs2.create_inode(is_dir=True)  # root
        fs2 = golden_create(fs2, '/bar', is_dir=True)
        fs2 = golden_create(fs2, '/bar/baz', is_dir=True)

        fs_nested_deleted = delete(fs2, '/bar/baz')
        try:
            golden_read(fs_nested_deleted, '/bar/baz', 0, 1)
            details['delete_nested'] = False
        except FileNotFoundError:
            details['delete_nested'] = True
            score += 10

        fs_parent_deleted = delete(fs_nested_deleted, '/bar')
        try:
            golden_read(fs_parent_deleted, '/bar', 0, 1)
            details['delete_parent'] = False
        except FileNotFoundError:
            details['delete_parent'] = True
            score += 10
    except Exception:
        details['delete_nested'] = details.get('delete_nested', False)
        details['delete_parent'] = details.get('delete_parent', False)

    # 3) FileNotFoundError
    try:
        sb3 = SuperBlock(block_size=512, total_blocks=16, inode_count=16,
                         free_block_bitmap=[True]*16)
        fs3 = FileSystemImage(sb3)
        fs3.create_inode(is_dir=True)
        try:
            delete(fs3, '/nonexistent')
            details['fnf_error'] = False
        except FileNotFoundError:
            details['fnf_error'] = True
            score += 20
    except Exception:
        details['fnf_error'] = False

    # 4) NotADirectoryError
    try:
        sb4 = SuperBlock(block_size=512, total_blocks=16, inode_count=16,
                         free_block_bitmap=[True]*16)
        fs4 = FileSystemImage(sb4)
        fs4.create_inode(is_dir=True)
        fs4 = golden_create(fs4, '/file.txt', is_dir=False)
        try:
            delete(fs4, '/file.txt/sub')
            details['not_directory_error'] = False
        except NotADirectoryError:
            details['not_directory_error'] = True
            score += 20
    except Exception:
        details['not_directory_error'] = False

    # 5) OSError
    try:
        sb5 = SuperBlock(block_size=512, total_blocks=16, inode_count=16,
                         free_block_bitmap=[True]*16)
        fs5 = FileSystemImage(sb5)
        fs5.create_inode(is_dir=True)
        fs5 = golden_create(fs5, '/dir', is_dir=True)
        fs5 = golden_create(fs5, '/dir/file', is_dir=False)
        try:
            delete(fs5, '/dir')
            details['dir_not_empty_error'] = False
        except OSError:
            details['dir_not_empty_error'] = True
            score += 20
    except Exception:
        details['dir_not_empty_error'] = False
    passed = (score == 100)
    
    return passed, details, score, confidence

