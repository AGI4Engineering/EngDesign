import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from solution import gold_create, gold_read, gold_write, gold_delete

@dataclass
class SuperBlock:
    """File system superblock, stores metadata."""
    block_size: int             # Size of each block (bytes)
    total_blocks: int           # Total number of blocks
    inode_count: int            # Total number of inodes
    free_block_bitmap: List[bool]  # Free block bitmap, True = free

@dataclass
class Inode:
    """Inode structure, stores file/directory metadata."""
    ino: int                    # Inode number
    is_dir: bool                # Whether this inode is a directory
    size: int                   # File size (bytes)
    direct_blocks: List[int]    # List of direct block indices
    # Optional: add indirect block pointers, multi-level indexing, permissions, timestamps, etc.

@dataclass
class DirEntry:
    """Directory entry: maps a filename to an inode."""
    name: str
    inode: int

@dataclass
class FileSystemImage:
    """Complete file system image structure."""
    superblock: SuperBlock
    inodes: Dict[int, Inode] = field(default_factory=dict)
    # Directory tree: inode -> list of entries in that directory; valid only for is_dir=True inodes
    directories: Dict[int, List[DirEntry]] = field(default_factory=dict)
    # Data block storage area: index corresponds to block number, content is bytes
    data_blocks: List[Optional[bytes]] = field(default_factory=list)

    def __post_init__(self):
        # Initialize data block storage area
        if not self.data_blocks:
            self.data_blocks = [None] * self.superblock.total_blocks

    def allocate_block(self) -> int:
        """Allocate a block from the free bitmap and return its index; raise if none available."""
        for idx, free in enumerate(self.superblock.free_block_bitmap):
            if free:
                self.superblock.free_block_bitmap[idx] = False
                self.data_blocks[idx] = b''  # Initialize with empty content
                return idx
        raise RuntimeError("No free blocks available")

    def free_block(self, block_idx: int):
        """Free the specified block index."""
        if 0 <= block_idx < self.superblock.total_blocks:
            self.superblock.free_block_bitmap[block_idx] = True
            self.data_blocks[block_idx] = None
        else:
            raise IndexError("Block index out of range")

    def create_inode(self, is_dir: bool) -> Inode:
        """Create a new inode and return it."""
        new_ino = len(self.inodes) + 1
        if new_ino > self.superblock.inode_count:
            raise RuntimeError("No free inodes")
        inode = Inode(
            ino=new_ino,
            is_dir=is_dir,
            size=0,
            direct_blocks=[]
        )
        self.inodes[new_ino] = inode
        if is_dir:
            self.directories[new_ino] = []
        return inode

    def add_dir_entry(self, dir_ino: int, name: str, inode: int):
        """Add a directory entry to the directory with inode dir_ino."""
        if dir_ino not in self.directories:
            raise RuntimeError("Not a directory inode")
        self.directories[dir_ino].append(DirEntry(name=name, inode=inode))


def evaluate_llm_response(llm_response):
    # try:
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
    details = {}
    try:
        exec(llm_response.config.write, namespace)
    except Exception as e:
        details['read'] = "Error in code execution: " + str(e)
        return False, details, 0, confidence

    
    write  = namespace['write']
    score = 0

    print("Testing file system operations write...")

    fs = gold_create(fs, "/test.txt", False)
    fs = gold_create(fs, "/test_dir", True)
    fs = gold_create(fs, "/test_dir/test.txt", False)
    
    # Test write operation
    try:
        fs = write(fs, "test_dir/test.txt", 0, "Hello World")
        details['write'] = "Write operation successful"
        score += 30
    except Exception as e:
        details['write'] = "Error in write operation: " + str(e)
        
    try:
        fs = write(fs, "test_dir/test.txt", 0, "Hello World")
        details['write'] = "Write operation successful"
        score += 30
    except Exception as e:
        details['write'] = "Error in write operation: " + str(e)
        
    # check with the content
    try:
        if gold_read(fs, "test_dir/test.txt", 0, 11) == "Hello World":
            details['read'] = "Read content is correct"
            score += 20
    except Exception as e:
        details['read'] = "Error in read content check "
        
    # test with invalid file
    try:
        fs = write(fs,"non_existent.txt", 0, "Hello World")
        details['write'] = "Error in write operation: No such file or directory"
    except Exception as e:
        details['write'] = "correctly raised error for non-existent file"
        score += 20
        

    passed = (score == 100)
    
    return passed, details, score, confidence
    # except Exception as e:
    #     return False, {"Error in code execution: " + str(e)}, None, None


