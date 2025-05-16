from dataclasses import dataclass, field
from typing import List, Dict, Optional


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

def golden_read(
    fs_img: FileSystemImage,
    name: str,
    pos: int,
    length: int
) -> str:
    if not name.startswith("/"):
        raise FileNotFoundError(f"Path must be absolute: {name}")
    parts = [p for p in name.split("/") if p]
    if not parts:
        raise IsADirectoryError("Cannot read root directory")

    ino = 1  # start at root inode
    for comp in parts:
        if ino not in fs_img.directories:
            raise FileNotFoundError(f"Component '{comp}' not found")
        entries = fs_img.directories[ino]
        match = next((e for e in entries if e.name == comp), None)
        if match is None:
            raise FileNotFoundError(f"Component '{comp}' not found")
        ino = match.inode

    inode = fs_img.inodes.get(ino)
    if inode is None:
        raise FileNotFoundError(f"No inode for path {name}")
    if inode.is_dir:
        raise IsADirectoryError(f"Is a directory: {name}")

    # --- 2. Validate offsets ---
    size = inode.size
    if pos < 0 or pos > size:
        raise ValueError(f"Invalid read offset {pos} for file size {size}")

    end = min(pos + length, size)
    to_read = end - pos
    if to_read <= 0:
        return ""  # nothing to read

    # --- 3. Read data blocks ---
    block_size = fs_img.superblock.block_size
    data = bytearray()
    # determine starting block and offset
    blk_idx = pos // block_size
    offset = pos % block_size

    while to_read > 0:
        if blk_idx >= len(inode.direct_blocks):
            break  # no more blocks
        block_num = inode.direct_blocks[blk_idx]
        blk_data = fs_img.data_blocks[block_num] or b""
        # read from offset up to either end of block or remaining bytes
        chunk = blk_data[offset : offset + to_read]
        data.extend(chunk)
        read_bytes = len(chunk)
        to_read -= read_bytes
        blk_idx += 1
        offset = 0  # only first block uses non-zero offset

    # --- 4. Decode and return ---
    return data.decode("utf-8")

def golden_write(
    fs_img: FileSystemImage,
    name: str,
    pos: int,
    data: str
) -> FileSystemImage:
    if not name.startswith("/"):
        raise FileNotFoundError(f"Path must be absolute: {name}")
    parts = [p for p in name.split("/") if p]
    if not parts:
        raise IsADirectoryError("Cannot write to root directory")

    ino = 1  # root inode
    for comp in parts:
        if ino not in fs_img.directories:
            raise FileNotFoundError(f"Component '{comp}' not found")
        entries = fs_img.directories[ino]
        match = next((e for e in entries if e.name == comp), None)
        if match is None:
            raise FileNotFoundError(f"Component '{comp}' not found")
        ino = match.inode

    inode = fs_img.inodes.get(ino)
    if inode is None:
        raise FileNotFoundError(f"No inode for path {name}")
    if inode.is_dir:
        raise IsADirectoryError(f"Is a directory: {name}")

    # --- 2. Validate pos ---
    old_size = inode.size
    if pos < 0 or pos > old_size:
        raise ValueError(f"Invalid write offset {pos} for file size {old_size}")

    # --- 3. Prepare data ---
    data_bytes = data.encode("utf-8")
    total_len = len(data_bytes)
    end_pos = pos + total_len

    block_size = fs_img.superblock.block_size

    # --- 4. Allocate new blocks if writing past EOF ---
    needed_blocks = (end_pos + block_size - 1) // block_size
    while len(inode.direct_blocks) < needed_blocks:
        blk = fs_img.allocate_block()
        inode.direct_blocks.append(blk)

    # --- 5. Write to blocks ---
    data_off = 0
    blk_idx = pos // block_size
    offset = pos % block_size

    while data_off < total_len:
        block_num = inode.direct_blocks[blk_idx]
        # get existing block content or initialize
        existing = fs_img.data_blocks[block_num]
        buf = bytearray(existing or b'\x00' * block_size)
        # how many bytes to write in this block
        chunk_len = min(block_size - offset, total_len - data_off)
        # write chunk
        buf[offset:offset + chunk_len] = data_bytes[data_off:data_off + chunk_len]
        # store back as bytes
        fs_img.data_blocks[block_num] = bytes(buf)
        # advance
        data_off += chunk_len
        blk_idx += 1
        offset = 0

    # --- 6. Update file size ---
    inode.size = max(old_size, end_pos)

    return fs_img
    
def golden_create(
    fs_img: FileSystemImage,
    path: str,
    is_dir: bool = False
) -> FileSystemImage:
    if not path.startswith("/"):
        raise ValueError("Path must be absolute")
    parts = [p for p in path.split("/") if p]
    if not parts:
        raise ValueError("Cannot create root")
    parent_parts, name = parts[:-1], parts[-1]

    # Traverse to find parent inode (start at root inode = 1)
    parent_ino = 1
    for comp in parent_parts:
        # must be a directory
        if parent_ino not in fs_img.directories:
            raise NotADirectoryError(f"Component '{comp}' is not a directory")
        # find entry
        entries = fs_img.directories[parent_ino]
        match = next((e for e in entries if e.name == comp), None)
        if match is None:
            raise FileNotFoundError(f"Directory '{comp}' not found")
        parent_ino = match.inode

    # Ensure parent is a directory
    if parent_ino not in fs_img.directories:
        raise NotADirectoryError("Parent path is not a directory")

    # Check for name collision
    for e in fs_img.directories[parent_ino]:
        if e.name == name:
            raise FileExistsError(f"Entry '{name}' already exists")

    # Allocate new inode
    new_inode = fs_img.create_inode(is_dir=is_dir)
    # Link into parent directory
    fs_img.add_dir_entry(parent_ino, name, new_inode.ino)

    return fs_img

def delete(
    fs_img: FileSystemImage,
    path: str
) -> FileSystemImage:
    if not path.startswith("/"):
        raise FileNotFoundError(f"Path must be absolute: {path}")
    parts = [p for p in path.split("/") if p]
    if not parts:
        raise FileNotFoundError("Cannot delete root")
    parent_parts, name = parts[:-1], parts[-1]

    # 2. Traverse to find parent inode
    parent_ino = 1
    for comp in parent_parts:
        if parent_ino not in fs_img.directories:
            raise NotADirectoryError(f"Component '{comp}' is not a directory")
        entries = fs_img.directories[parent_ino]
        match = next((e for e in entries if e.name == comp), None)
        if match is None:
            raise FileNotFoundError(f"Directory '{comp}' not found")
        parent_ino = match.inode

    # Ensure parent is a directory
    if parent_ino not in fs_img.directories:
        raise NotADirectoryError(f"Parent path is not a directory: {'/'.join(parent_parts)}")

    # 3. Locate entry in parent
    entries = fs_img.directories[parent_ino]
    entry = next((e for e in entries if e.name == name), None)
    if entry is None:
        raise FileNotFoundError(f"No such file or directory: {path}")
    target_ino = entry.inode

    # 4. Inspect target inode
    inode = fs_img.inodes.get(target_ino)
    if inode is None:
        raise FileNotFoundError(f"Inode {target_ino} missing for path {path}")

    if inode.is_dir:
        # directory: only delete if empty
        child_entries = fs_img.directories.get(target_ino, [])
        if child_entries:
            raise OSError("Directory not empty")
        # remove directory structure
        del fs_img.directories[target_ino]
    else:
        # file: free its data blocks
        for blk in inode.direct_blocks:
            fs_img.free_block(blk)

    # 5. Remove inode
    del fs_img.inodes[target_ino]

    # 6. Remove directory entry from parent
    fs_img.directories[parent_ino] = [
        e for e in fs_img.directories[parent_ino] if e.name != name
    ]

    return fs_img


    
