import math
import os
from block import Block
from cache import Cache

class Partition():
    '''
    A uniform partition of the array to be repartitioned. May be the array
    itself (partition of size 1), the input, output, read or write blocks.

    Attributes:
        shape: the shape of the blocks in the partition
        array: a partition with 1 block, representing the partitioned array (might be None)
        blocs: the list of blocks in the partition
        zeros: if True, fill all the blocks with zeros. Warning: this allocates memory. 
    '''

    def __init__(self, shape, name, array=None, fill=None, create_blocks=True):
        assert(all(x >= 0 for x in shape)), f"Invalid shape: {shape}"
        self.shape = tuple(shape)
        self.ndim = len(shape)
        self.name = name
        self.array = self

        # check that block shape is compatible with array dimension
        if array != None:
            self.array = array
            assert(array.ndim == self.ndim)
            assert(all(array.shape[i] % self.shape[i] == 0) for i in range(array.ndim))

        if create_blocks:
            self.blocks = self.__get_blocks(fill)

    def repartition(self, out_blocks, m, get_read_write_blocks):
        '''
        Fills partition out_blocks with data from self.
        out_blocks: a partition. The blocks of this partition will be written
        Return number of seeks done in the repartition
        '''
        log('')
        log(f'# Repartitioning {self.name} in {out_blocks.name}')
        read_blocks, cache = get_read_write_blocks(self, out_blocks, m, self.array)
        log(f'repartition: Selected read blocks: {read_blocks}')
        log(f'repartition: Cache: {cache}')
        seeks = 0
        total_bytes = 0
        for read_block in read_blocks.blocks:
            t, s = self.read_from(read_blocks.blocks[read_block])
            log(f'repartition: Read required {s} seeks')
            total_bytes += t
            seeks += s
            complete_blocks = cache.insert(read_blocks.blocks[read_block])
            for b in complete_blocks:
                log(f'repartition: Writing complete block {b}')
                # TODO: it's a bit overkill to write_to all the output blocks
                # although nothing is actually written to blocks that don't need it
                # Also, write_to is not well named, it is the block being written
                # to the partition
                t, s = out_blocks.write_to(b)
                log(f'repartition: Write required {s} seeks')
                total_bytes += t
                seeks += s
                b.clear()
        return total_bytes, seeks

    def read_from(self, block):
        '''
        Read block from partition. Shape of block may not match shape of 
        partition.
        '''
        seeks = 0
        total_bytes = 0
        if block.shape == self.shape:
            # Return partition block
            my_block = self.blocks[block.origin]
            total_bytes = my_block.read()
            block.data = my_block.data
            seeks = 1
        else:
            for b in self.blocks:
                t, s = block.read_from(self.blocks[b])
                seeks += s
                total_bytes += t
        return total_bytes, seeks
    
    def write_to(self, block):
        '''
        Write data in block to partition blocks. Shape of block may not match
        shape of partition.
        '''
        seeks = 0
        total_bytes = 0
        if block.shape == self.shape:
            # Return partition block
            my_block = self.blocks[block.origin]
            my_block.data = block.data
            total_bytes = my_block.write()
            seeks = 1
        else:
            for b in self.blocks:
                t, s = block.write_to(self.blocks[b])
                seeks += s
                total_bytes += t
        return total_bytes, seeks

    def write(self):
        for b in self.blocks:
            self.blocks[b].write()

    def clear(self):
        for b in self.blocks:
            self.blocks[b].clear()

    def __get_blocks(self, fill):
        '''
        Return the list of blocks in this partition
        '''

        # The partition is the array itself
        if self.array == None:
            return { (0, 0, 0): Block((0, 0, 0), self.shape, fill=fill, file_name=f'{self.name}.bin') }

        blocks = {}
        shape = self.array.shape
        # Warning: read order of blocks in repartition
        # depends on this key order...
        ni = int(shape[0]/self.shape[0])
        nj = int(shape[1]/self.shape[1])
        nk = int(shape[2]/self.shape[2])
        blocks = { (i*self.shape[0], j*self.shape[1], k*self.shape[2]):
                   Block((i*self.shape[0], j*self.shape[1], k*self.shape[2]), self.shape,
                          fill=fill, file_name=f'{self.name}_block_{math.prod(self.shape)*(k+j*nk+i*nj*nk)}.bin') 
                    for i in range(ni)
                    for j in range(nj)
                    for k in range(nk)
                 }
        return blocks

    def get_neighbor_block_ind(self, block_ind, dim):
        '''
        Return the index of the neighbor block of block index block_ind along dimension dim, in positive orientation.
        '''
        array_shape = self.array.shape
        n_blocks = [ int(array_shape[i]/self.shape[i]) for i in range(len(self.shape))]
        if dim == 2:
            neighbor_ind = block_ind + 1
        if dim == 1:
            neighbor_ind = block_ind + n_blocks[2]
        if dim == 0:
            neighbor_ind = block_ind + n_blocks[2]*n_blocks[1]
        return neighbor_ind

    def __str__(self):

        blocks = os.linesep.join([str(self.blocks[b]) for b in self.blocks])

        if self.array is None:
            return f'Partition of shape {self.shape}. Blocks:' + os.linesep + blocks
        else:
            return f'Partition of shape {self.shape} of array of shape {self.array.shape}. Blocks:' + os.linesep + blocks

def log(message, level=0):
    LOG_LEVEL=1
    if level >= LOG_LEVEL:
        print(message)