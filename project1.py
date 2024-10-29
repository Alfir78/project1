#!/usr/bin/python3

"""
CS-UY 2214
Adapted from Jeff Epstein
Starter code for E20 simulator
sim.py
"""

from collections import namedtuple
import re
import argparse

# Some helpful constant values that we'll be using.
Constants = namedtuple("Constants",["NUM_REGS", "MEM_SIZE", "REG_SIZE"])
constants = Constants(NUM_REGS = 8,
                      MEM_SIZE = 2**13,
                      REG_SIZE = 2**16)

def load_machine_code(machine_code, mem):
    """
    Loads an E20 machine code file into the list
    provided by mem. We assume that mem is
    large enough to hold the values in the machine
    code file.
    sig: list(str) -> list(int) -> NoneType
    """
    machine_code_re = re.compile("^ram\[(\d+)\] = 16'b(\d+);.*$")
    expectedaddr = 0
    for line in machine_code:
        match = machine_code_re.match(line)
        if not match:
            raise ValueError("Can't parse line: %s" % line)
        addr, instr = match.groups()
        addr = int(addr,10)
        instr = int(instr,2)
        if addr != expectedaddr:
            raise ValueError("Memory addresses encountered out of sequence: %s" % addr)
        if addr >= len(mem):
            raise ValueError("Program too big for memory")
        expectedaddr += 1
        mem[addr] = instr


def print_state(pc, regs, memory, memquantity):
    """
    Prints the current state of the simulator, including
    the program counter, the register values, and memory.
    """
    print("Final state:")
    print("\tpc=" + format(pc, "5d"))
    for reg, regval in enumerate(regs):
        print(("\t$%s=" % reg) + format(regval, "5d"))
    line = ""
    for count in range(memquantity):
        line += format(memory[count], "04x") + " "
        if count % 8 == 7:
            print(line)
            line = ""
    if line != "":
        print(line)

def execute_instruction(instr, pc, regs, memory):
    """
    Decodes and executes a single E20 instruction.
    Returns the updated program counter.
    """
    opcode = (instr >> 13) & 0b111   # Extract the opcode (first 3 bits)
    r_dest = (instr >> 10) & 0b111   # Destination register
    r_src1 = (instr >> 7) & 0b111    # Source register 1
    r_src2 = (instr >> 4) & 0b111    # Source register 2
    imm = instr & 0xF                # Immediate value (last 4 bits)

    if opcode == 0b000:  # add
        regs[r_dest] = (regs[r_src1] + regs[r_src2]) % constants.REG_SIZE
        pc += 1
    elif opcode == 0b001:  # addi
        regs[r_dest] = (regs[r_src1] + imm) % constants.REG_SIZE
        pc += 1
    elif opcode == 0b010:  # sub
        regs[r_dest] = (regs[r_src1] - regs[r_src2]) % constants.REG_SIZE
        pc += 1
    elif opcode == 0b011:  # subi
        regs[r_dest] = (regs[r_src1] - imm) % constants.REG_SIZE
        pc += 1
    elif opcode == 0b100:  # lw (load word)
        regs[r_dest] = memory[regs[r_src1] + imm]
        pc += 1
    elif opcode == 0b101:  # sw (store word)
        memory[regs[r_src1] + imm] = regs[r_dest]
        pc += 1
    elif opcode == 0b110:  # slt (set less than)
        regs[r_dest] = 1 if regs[r_src1] < regs[r_src2] else 0
        pc += 1
    elif opcode == 0b111:  # jeq (jump if equal)
        if regs[r_src1] == regs[r_src2]:
            pc = regs[r_dest]
        else:
            pc += 1
    elif opcode == 0b0000:  # halt
        pc = -1  # Signal to end the program
    else:
        raise ValueError("Unknown opcode: %s" % opcode)
    return pc

def main():
    parser = argparse.ArgumentParser(description='Simulate E20 machine')
    parser.add_argument('filename', help='The file containing machine code, typically with .bin suffix')
    cmdline = parser.parse_args()

    # Initialize memory and registers
    memory = [0] * constants.MEM_SIZE
    regs = [0] * constants.NUM_REGS
    pc = 0

    # Load the machine code into memory
    with open(cmdline.filename) as file:
        load_machine_code(file, memory)

    # Run the simulation
    while pc != -1:
        instr = memory[pc]
        pc = execute_instruction(instr, pc, regs, memory)

    # Print the final state of the simulator
    print_state(pc, regs, memory, 128)  # Print first 128 memory cells in hex

if __name__ == "__main__":
    main()
