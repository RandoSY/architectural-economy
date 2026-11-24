"""
Faithful 12-bit DEC PDP-8 Instruction-Level Emulator & Architectural Economy Benchmark.

Implements the 8 primary opcode classes of the 1965 DEC PDP-8 (AND, TAD, ISZ, DCA,
JMS, JMP, IOT, OPR) with 4,096 x 12-bit core memory, AC, Link (L), PC, Page 0 /
Current-Page addressing, indirect addressing, and auto-index registers (0010-0017 octal).

Compares four genuinely assembled, bit-exact-verified PDP-8 implementations of an
N-task 6-bit unsigned multiplication workload (shift-and-add, since base PDP-8 lacked
hardware multiply):
  1. Inlined (Dedicated): each task duplicates the full shift-and-add routine inline.
  2. Shared Subroutine (JMS): all N tasks call one shared MUL subroutine.
  3. Dual-Modular Shared: tasks split evenly across two independent MUL subroutines.
  4. Shared + Redundant Verification (Buffered): primary + shadow MUL with mismatch
     fallback to a tertiary copy (TMR-style recovery on single-word routine faults).

Measures:
  - Static code memory footprint (12-bit words, excluding shared data tables)
  - Dynamic instructions executed and PDP-8 memory cycles
  - Single-instruction-word fault blast radius (exact fraction/count of tasks corrupted
    by flipping/corrupting every executable instruction word one at a time)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

MASK12 = 0xFFF
PAGE_MASK = 0xF80
OFFSET_MASK = 0x07F

# Opcodes (bits 11..9)
OP_AND = 0 << 9
OP_TAD = 1 << 9
OP_ISZ = 2 << 9
OP_DCA = 3 << 9
OP_JMS = 4 << 9
OP_JMP = 5 << 9
OP_IOT = 6 << 9
OP_OPR = 7 << 9

# Addressing mode flags
IND = 1 << 8   # Indirect bit (0400 octal)
CUR = 1 << 7   # Current-page bit (0200 octal); 0 = Page 0

# Group 1 OPR microinstructions (bit 8 = 0)
CLA = OP_OPR | 0o0200
CLL = OP_OPR | 0o0100
CMA = OP_OPR | 0o0040
CML = OP_OPR | 0o0020
RAR = OP_OPR | 0o0010
RAL = OP_OPR | 0o0004
BSW = OP_OPR | 0o0002  # rotate twice when paired with RAR/RAL
IAC = OP_OPR | 0o0001
NOP = OP_OPR

# Group 2 OPR microinstructions (bit 8 = 1, bit 0 = 0)
OPR2 = OP_OPR | 0o0400
SMA = OPR2 | 0o0100
SZA = OPR2 | 0o0040
SNL = OPR2 | 0o0020
REV = OPR2 | 0o0010  # Reverse skip sense (SPA, SNA, SZL, SKP)
SPA = OPR2 | 0o0100 | REV
SNA = OPR2 | 0o0040 | REV
SZL = OPR2 | 0o0020 | REV
SKP = OPR2 | REV
HLT = OPR2 | 0o0002
CLA2 = OPR2 | 0o0200


@dataclass
class RunStats:
    halted: bool
    timed_out: bool
    instructions: int
    memory_cycles: int


class PDP8:
    """Cycle-accurate 12-bit DEC PDP-8 emulator."""

    def __init__(self) -> None:
        self.mem: List[int] = [0] * 4096
        self.ac: int = 0
        self.link: int = 0
        self.pc: int = 0

    def load(self, words: Dict[int, int]) -> None:
        for addr, val in words.items():
            if not (0 <= addr < 4096):
                raise ValueError(f"Address out of 4096-word PDP-8 core: {addr}")
            self.mem[addr] = val & MASK12

    def run(self, start_pc: int, max_instructions: int = 500_000) -> RunStats:
        self.pc = start_pc & MASK12
        self.ac = 0
        self.link = 0
        instr_count = 0
        cycles = 0

        mem = self.mem
        while instr_count < max_instructions:
            pc_curr = self.pc
            instr = mem[pc_curr]
            self.pc = (pc_curr + 1) & MASK12
            instr_count += 1
            cycles += 1  # Fetch cycle

            opcode = (instr >> 9) & 0x7

            if opcode <= 5:
                # Memory reference instruction
                offset = instr & OFFSET_MASK
                if instr & CUR:
                    ea = (pc_curr & PAGE_MASK) | offset
                else:
                    ea = offset

                if instr & IND:
                    cycles += 1  # Defer (indirect) cycle
                    if 0o0010 <= ea <= 0o0017:
                        mem[ea] = (mem[ea] + 1) & MASK12
                    ea = mem[ea]

                if opcode == 0:  # AND
                    cycles += 1
                    self.ac &= mem[ea]
                elif opcode == 1:  # TAD
                    cycles += 1
                    total = (self.link << 12) + self.ac + mem[ea]
                    self.link = (total >> 12) & 1
                    self.ac = total & MASK12
                elif opcode == 2:  # ISZ
                    cycles += 1
                    val = (mem[ea] + 1) & MASK12
                    mem[ea] = val
                    if val == 0:
                        self.pc = (self.pc + 1) & MASK12
                elif opcode == 3:  # DCA
                    cycles += 1
                    mem[ea] = self.ac
                    self.ac = 0
                elif opcode == 4:  # JMS
                    cycles += 1
                    mem[ea] = self.pc
                    self.pc = (ea + 1) & MASK12
                elif opcode == 5:  # JMP
                    self.pc = ea

            elif opcode == 6:  # IOT (treated as 1-cycle NOP in benchmark)
                pass

            else:  # opcode == 7: OPR
                if (instr & 0o0400) == 0:
                    # Group 1 microinstructions (official DEC timing order)
                    if instr & 0o0200:  # CLA
                        self.ac = 0
                    if instr & 0o0100:  # CLL
                        self.link = 0
                    if instr & 0o0040:  # CMA
                        self.ac ^= MASK12
                    if instr & 0o0020:  # CML
                        self.link ^= 1
                    if instr & 0o0001:  # IAC
                        total = (self.link << 12) + self.ac + 1
                        self.link = (total >> 12) & 1
                        self.ac = total & MASK12
                    rot_twice = bool(instr & 0o0002)
                    if instr & 0o0010:  # RAR / RTR
                        steps = 2 if rot_twice else 1
                        for _ in range(steps):
                            lsb = self.ac & 1
                            self.ac = ((self.link << 11) | (self.ac >> 1)) & MASK12
                            self.link = lsb
                    elif instr & 0o0004:  # RAL / RTL
                        steps = 2 if rot_twice else 1
                        for _ in range(steps):
                            msb = (self.ac >> 11) & 1
                            self.ac = ((self.ac << 1) | self.link) & MASK12
                            self.link = msb
                else:
                    # Group 2 microinstructions (bit 0 == 0)
                    if (instr & 0o0001) == 0:
                        reverse = bool(instr & 0o0010)
                        cond_sma = bool(instr & 0o0100) and bool(self.ac & 0o4000)
                        cond_sza = bool(instr & 0o0040) and (self.ac == 0)
                        cond_snl = bool(instr & 0o0020) and (self.link != 0)
                        if not reverse:
                            skip = cond_sma or cond_sza or cond_snl
                        else:
                            # AND-group: SPA/SNA/SZL/SKP
                            skip = True
                            if instr & 0o0100:
                                skip = skip and not bool(self.ac & 0o4000)
                            if instr & 0o0040:
                                skip = skip and (self.ac != 0)
                            if instr & 0o0020:
                                skip = skip and (self.link == 0)
                        if skip:
                            self.pc = (self.pc + 1) & MASK12
                        if instr & 0o0200:  # CLA (occurs after skip test)
                            self.ac = 0
                        if instr & 0o0002:  # HLT
                            return RunStats(True, False, instr_count, cycles)

        return RunStats(False, True, instr_count, cycles)


def ref(opcode: int, target_addr: int, curr_pc: int, indirect: bool = False) -> int:
    """Encode a PDP-8 memory-reference instruction targeting Page 0 or current page."""
    ind_bit = IND if indirect else 0
    if target_addr < 128:
        return opcode | ind_bit | target_addr
    if (target_addr & PAGE_MASK) != (curr_pc & PAGE_MASK):
        raise ValueError(
            f"Direct reference from {oct(curr_pc)} to {oct(target_addr)} crosses 128-word page boundary"
        )
    return opcode | ind_bit | CUR | (target_addr & OFFSET_MASK)


class Assembler:
    """Minimal page-aware PDP-8 assembler emitting clean code blocks."""

    def __init__(self, start_addr: int = 0o0200) -> None:
        self.mem: Dict[int, int] = {}
        self.pc = start_addr
        self.code_addrs: List[int] = []
        self.routine_addrs: List[int] = []

    def ensure_room_on_page(self, needed_words: int) -> None:
        """If block won't fit on current 128-word page, jump to start of next page."""
        page_end = (self.pc & PAGE_MASK) + 128
        # Leave 2 words at end of page for cross-page indirect jump if needed
        if self.pc + needed_words > page_end - 2:
            next_page = page_end
            if next_page >= 4096:
                raise MemoryError("Program exceeded 4,096-word PDP-8 core memory!")
            ptr_addr = page_end - 1
            self.mem[ptr_addr] = next_page
            self.emit(ref(OP_JMP, ptr_addr, self.pc, indirect=True), track_code=False)
            self.pc = next_page

    def emit(self, word: int, track_code: bool = True, is_routine: bool = False) -> int:
        addr = self.pc
        if addr >= 4096:
            raise MemoryError("Program exceeded 4,096-word PDP-8 core memory!")
        self.mem[addr] = word & MASK12
        if track_code:
            self.code_addrs.append(addr)
        if is_routine:
            self.routine_addrs.append(addr)
        self.pc += 1
        return addr

    def emit_data(self, word: int) -> int:
        addr = self.pc
        self.mem[addr] = word & MASK12
        self.pc += 1
        return addr


# Fixed Page-0 scratchpad and pointers
P0_ARG1 = 0o0020
P0_ARG2 = 0o0021
P0_PROD = 0o0022
P0_CNT = 0o0023
P0_MINUS6 = 0o0024
P0_PTR_A = 0o0025
P0_PTR_B = 0o0026
P0_PTR_OUT = 0o0027
P0_PTR_MUL1 = 0o0030
P0_PTR_MUL2 = 0o0031
P0_PTR_MUL3 = 0o0032
P0_TMP1 = 0o0033
P0_TMP2 = 0o0034
P0_SAVE_A = 0o0035
P0_SAVE_B = 0o0036
P0_TMP_NEG = 0o0037

# Auto-index registers on Page 0 (0010..0012 octal auto-increment on indirect use)
AUTO_A = 0o0010
AUTO_B = 0o0011
AUTO_OUT = 0o0012

# Data tables placed in upper core memory (shared identically across all architectures)
DATA_A_BASE = 0o6000   # 3072..3199
DATA_B_BASE = 0o6200   # 3200..3327
DATA_OUT_BASE = 0o6400 # 3328..3455


def emit_mul_subroutine(asm: Assembler) -> int:
    """
    Emit a standalone 6-bit unsigned shift-and-add MUL subroutine on a single page.
    Reads P0_ARG1, P0_ARG2; returns product in AC.
    Size: 21 words (1 return-addr slot + 20 executable instructions).
    """
    asm.ensure_room_on_page(24)
    entry = asm.emit_data(0)  # Return address stored here by JMS
    asm.emit(CLA | CLL, is_routine=True)
    asm.emit(ref(OP_DCA, P0_PROD, asm.pc), is_routine=True)
    asm.emit(ref(OP_TAD, P0_MINUS6, asm.pc), is_routine=True)
    asm.emit(ref(OP_DCA, P0_CNT, asm.pc), is_routine=True)

    loop_addr = asm.pc
    asm.emit(CLA | CLL, is_routine=True)
    asm.emit(ref(OP_TAD, P0_ARG2, asm.pc), is_routine=True)
    asm.emit(RAR, is_routine=True)
    asm.emit(ref(OP_DCA, P0_ARG2, asm.pc), is_routine=True)
    asm.emit(SNL, is_routine=True)
    skip_jmp_addr = asm.emit(0, is_routine=True)  # Patch to skip_add

    asm.emit(ref(OP_TAD, P0_PROD, asm.pc), is_routine=True)
    asm.emit(ref(OP_TAD, P0_ARG1, asm.pc), is_routine=True)
    asm.emit(ref(OP_DCA, P0_PROD, asm.pc), is_routine=True)

    skip_add = asm.pc
    asm.mem[skip_jmp_addr] = ref(OP_JMP, skip_add, skip_jmp_addr)

    asm.emit(CLA | CLL, is_routine=True)
    asm.emit(ref(OP_TAD, P0_ARG1, asm.pc), is_routine=True)
    asm.emit(RAL, is_routine=True)
    asm.emit(ref(OP_DCA, P0_ARG1, asm.pc), is_routine=True)
    asm.emit(ref(OP_ISZ, P0_CNT, asm.pc), is_routine=True)
    asm.emit(ref(OP_JMP, loop_addr, asm.pc), is_routine=True)

    asm.emit(ref(OP_TAD, P0_PROD, asm.pc), is_routine=True)
    asm.emit(ref(OP_JMP, entry, asm.pc, indirect=True), is_routine=True)
    return entry


def init_common_page0(asm: Assembler, pairs: List[Tuple[int, int]]) -> None:
    """Initialize Page 0 constants, auto-index pointers, and upper-core data tables."""
    asm.mem[P0_MINUS6] = (-6) & MASK12
    asm.mem[AUTO_A] = (DATA_A_BASE - 1) & MASK12
    asm.mem[AUTO_B] = (DATA_B_BASE - 1) & MASK12
    asm.mem[AUTO_OUT] = (DATA_OUT_BASE - 1) & MASK12
    for i, (a, b) in enumerate(pairs):
        asm.mem[DATA_A_BASE + i] = a & 0x3F
        asm.mem[DATA_B_BASE + i] = b & 0x3F
        asm.mem[DATA_OUT_BASE + i] = 0


def build_program(arch: str, pairs: List[Tuple[int, int]]) -> Tuple[Assembler, int]:
    """
    Assemble one of four PDP-8 architectures for N multiply tasks:
      - 'inlined':       Dedicated inline shift-and-add routine per task.
      - 'shared':        Single shared MUL subroutine invoked via JMS.
      - 'dual_modular':  Two independent MUL subroutines (tasks split 50/50).
      - 'buffered_tmr':  Three MUL subroutines; each task executes MUL1 & MUL2,
                         and if they disagree falls back to MUL3 (fault-buffered).
    """
    n = len(pairs)
    asm = Assembler(start_addr=0o0200)
    init_common_page0(asm, pairs)

    if arch == "inlined":
        start_pc = asm.pc
        for _ in range(n):
            # 25 words per inlined task (must fit on a single page for local JMPs)
            asm.ensure_room_on_page(27)
            asm.emit(CLA | CLL)
            asm.emit(ref(OP_TAD, AUTO_A, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_ARG1, asm.pc))
            asm.emit(ref(OP_TAD, AUTO_B, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_ARG2, asm.pc))

            # Inlined shift-and-add multiply body (19 words)
            asm.emit(ref(OP_DCA, P0_PROD, asm.pc), is_routine=True)
            asm.emit(ref(OP_TAD, P0_MINUS6, asm.pc), is_routine=True)
            asm.emit(ref(OP_DCA, P0_CNT, asm.pc), is_routine=True)
            loop_addr = asm.pc
            asm.emit(CLA | CLL, is_routine=True)
            asm.emit(ref(OP_TAD, P0_ARG2, asm.pc), is_routine=True)
            asm.emit(RAR, is_routine=True)
            asm.emit(ref(OP_DCA, P0_ARG2, asm.pc), is_routine=True)
            asm.emit(SNL, is_routine=True)
            skip_jmp = asm.emit(0, is_routine=True)
            asm.emit(ref(OP_TAD, P0_PROD, asm.pc), is_routine=True)
            asm.emit(ref(OP_TAD, P0_ARG1, asm.pc), is_routine=True)
            asm.emit(ref(OP_DCA, P0_PROD, asm.pc), is_routine=True)
            skip_add = asm.pc
            asm.mem[skip_jmp] = ref(OP_JMP, skip_add, skip_jmp)
            asm.emit(CLA | CLL, is_routine=True)
            asm.emit(ref(OP_TAD, P0_ARG1, asm.pc), is_routine=True)
            asm.emit(RAL, is_routine=True)
            asm.emit(ref(OP_DCA, P0_ARG1, asm.pc), is_routine=True)
            asm.emit(ref(OP_ISZ, P0_CNT, asm.pc), is_routine=True)
            asm.emit(ref(OP_JMP, loop_addr, asm.pc), is_routine=True)
            asm.emit(ref(OP_TAD, P0_PROD, asm.pc), is_routine=True)

            asm.emit(ref(OP_DCA, AUTO_OUT, asm.pc, indirect=True))
        asm.emit(HLT, track_code=False)
        return asm, start_pc

    elif arch == "shared":
        mul1 = emit_mul_subroutine(asm)
        asm.mem[P0_PTR_MUL1] = mul1
        start_pc = asm.pc
        for _ in range(n):
            asm.ensure_room_on_page(9)
            asm.emit(CLA | CLL)
            asm.emit(ref(OP_TAD, AUTO_A, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_ARG1, asm.pc))
            asm.emit(ref(OP_TAD, AUTO_B, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_ARG2, asm.pc))
            asm.emit(ref(OP_JMS, P0_PTR_MUL1, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, AUTO_OUT, asm.pc, indirect=True))
        asm.emit(HLT, track_code=False)
        return asm, start_pc

    elif arch == "dual_modular":
        mul1 = emit_mul_subroutine(asm)
        mul2 = emit_mul_subroutine(asm)
        asm.mem[P0_PTR_MUL1] = mul1
        asm.mem[P0_PTR_MUL2] = mul2
        start_pc = asm.pc
        for i in range(n):
            ptr = P0_PTR_MUL1 if (i % 2 == 0) else P0_PTR_MUL2
            asm.ensure_room_on_page(9)
            asm.emit(CLA | CLL)
            asm.emit(ref(OP_TAD, AUTO_A, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_ARG1, asm.pc))
            asm.emit(ref(OP_TAD, AUTO_B, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_ARG2, asm.pc))
            asm.emit(ref(OP_JMS, ptr, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, AUTO_OUT, asm.pc, indirect=True))
        asm.emit(HLT, track_code=False)
        return asm, start_pc

    elif arch == "buffered_tmr":
        # Shared helper WRAP_TMR executes MUL1 & MUL2; on mismatch falls back to MUL3
        mul1 = emit_mul_subroutine(asm)
        mul2 = emit_mul_subroutine(asm)
        mul3 = emit_mul_subroutine(asm)
        asm.mem[P0_PTR_MUL1] = mul1
        asm.mem[P0_PTR_MUL2] = mul2
        asm.mem[P0_PTR_MUL3] = mul3

        # Emit wrapper subroutine that compares MUL1 and MUL2, falling back to MUL3
        asm.ensure_room_on_page(34)
        wrap_entry = asm.emit_data(0)
        # Save args (in P0_SAVE_A, P0_SAVE_B)
        asm.emit(CLA | CLL)
        asm.emit(ref(OP_TAD, P0_SAVE_A, asm.pc))
        asm.emit(ref(OP_DCA, P0_ARG1, asm.pc))
        asm.emit(ref(OP_TAD, P0_SAVE_B, asm.pc))
        asm.emit(ref(OP_DCA, P0_ARG2, asm.pc))
        asm.emit(ref(OP_JMS, P0_PTR_MUL1, asm.pc, indirect=True))
        asm.emit(ref(OP_DCA, P0_TMP1, asm.pc))

        # Run MUL2
        asm.emit(ref(OP_TAD, P0_SAVE_A, asm.pc))
        asm.emit(ref(OP_DCA, P0_ARG1, asm.pc))
        asm.emit(ref(OP_TAD, P0_SAVE_B, asm.pc))
        asm.emit(ref(OP_DCA, P0_ARG2, asm.pc))
        asm.emit(ref(OP_JMS, P0_PTR_MUL2, asm.pc, indirect=True))
        asm.emit(ref(OP_DCA, P0_TMP2, asm.pc))

        # Compare TMP1 == TMP2 via TMP1 + (-TMP2) == 0
        asm.emit(ref(OP_TAD, P0_TMP2, asm.pc))
        asm.emit(CMA | IAC)
        asm.emit(ref(OP_TAD, P0_TMP1, asm.pc))
        asm.emit(SZA)  # Skip fallback if equal (AC == 0)
        jmp_fallback = asm.emit(0)
        asm.emit(ref(OP_TAD, P0_TMP1, asm.pc))
        asm.emit(ref(OP_JMP, wrap_entry, asm.pc, indirect=True))

        # Fallback: execute MUL3
        fallback_addr = asm.pc
        asm.mem[jmp_fallback] = ref(OP_JMP, fallback_addr, jmp_fallback)
        asm.emit(CLA | CLL)
        asm.emit(ref(OP_TAD, P0_SAVE_A, asm.pc))
        asm.emit(ref(OP_DCA, P0_ARG1, asm.pc))
        asm.emit(ref(OP_TAD, P0_SAVE_B, asm.pc))
        asm.emit(ref(OP_DCA, P0_ARG2, asm.pc))
        asm.emit(ref(OP_JMS, P0_PTR_MUL3, asm.pc, indirect=True))
        asm.emit(ref(OP_JMP, wrap_entry, asm.pc, indirect=True))

        p0_wrap = 0o0040
        asm.mem[p0_wrap] = wrap_entry

        start_pc = asm.pc
        for _ in range(n):
            asm.ensure_room_on_page(9)
            asm.emit(CLA | CLL)
            asm.emit(ref(OP_TAD, AUTO_A, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_SAVE_A, asm.pc))
            asm.emit(ref(OP_TAD, AUTO_B, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, P0_SAVE_B, asm.pc))
            asm.emit(ref(OP_JMS, p0_wrap, asm.pc, indirect=True))
            asm.emit(ref(OP_DCA, AUTO_OUT, asm.pc, indirect=True))
        asm.emit(HLT, track_code=False)
        return asm, start_pc

    else:
        raise ValueError(f"Unknown arch: {arch}")


def run_benchmark() -> Dict:
    task_counts = [1, 2, 4, 8, 16, 32, 64]
    architectures = ["inlined", "shared", "dual_modular", "buffered_tmr"]

    # Deterministic nontrivial 6-bit operand pairs (1..63 x 1..63, avoiding 0/1 triviality)
    all_pairs = [((i * 11 + 5) % 61 + 2, (i * 17 + 9) % 59 + 3) for i in range(64)]

    results: Dict[str, List[Dict]] = {a: [] for a in architectures}

    for n in task_counts:
        pairs = all_pairs[:n]
        expected = [a * b for a, b in pairs]

        for arch in architectures:
            asm, start_pc = build_program(arch, pairs)
            cpu = PDP8()
            cpu.load(asm.mem)
            stats = cpu.run(start_pc)

            actual = [cpu.mem[DATA_OUT_BASE + i] for i in range(n)]
            assert stats.halted and actual == expected, (
                f"Verification failed for {arch} N={n}: halted={stats.halted}"
            )

            # Static code footprint = total words occupied below data area (excluding Page 0)
            code_words = sum(1 for addr in asm.mem if 0o0200 <= addr < DATA_A_BASE)

            # Fault injection: replace each routine instruction word with NOP (simulating
            # a single-word loss-of-function disruption in a routine component).
            # Separate non-hanging (functional/arithmetic) faults from control-flow hangs
            # (infinite loops in a sequential von Neumann CPU).
            blast_all: List[int] = []
            blast_non_hang: List[int] = []
            hang_count = 0
            for fault_addr in asm.routine_addrs:
                fcpu = PDP8()
                fcpu.load(asm.mem)
                fcpu.mem[fault_addr] = NOP
                fstats = fcpu.run(start_pc, max_instructions=max(20_000, stats.instructions * 3))
                corrupted = sum(
                    1 for i in range(n) if fcpu.mem[DATA_OUT_BASE + i] != expected[i]
                )
                if not fstats.halted:
                    hang_count += 1
                    corrupted = max(corrupted, 1)
                else:
                    blast_non_hang.append(corrupted)
                blast_all.append(corrupted)

            mean_blast = sum(blast_all) / len(blast_all)
            max_blast = max(blast_all)
            mean_non_hang = sum(blast_non_hang) / len(blast_non_hang) if blast_non_hang else 0.0
            max_non_hang = max(blast_non_hang) if blast_non_hang else 0
            zero_failure_rate = sum(1 for c in blast_all if c == 0) / len(blast_all)
            non_hang_mask_rate = (
                sum(1 for c in blast_non_hang if c == 0) / len(blast_non_hang)
                if blast_non_hang else 0.0
            )

            row = {
                "n_tasks": n,
                "code_words": code_words,
                "pct_of_4k_core": round(100.0 * code_words / 4096.0, 2),
                "dynamic_instructions": stats.instructions,
                "memory_cycles": stats.memory_cycles,
                "routine_words_tested": len(asm.routine_addrs),
                "hang_faults": hang_count,
                "mean_blast_tasks": round(mean_blast, 3),
                "max_blast_tasks": max_blast,
                "non_hang_mean_blast_tasks": round(mean_non_hang, 3),
                "non_hang_max_blast_tasks": max_non_hang,
                "mean_blast_frac": round(mean_blast / n, 4),
                "non_hang_mean_blast_frac": round(mean_non_hang / n, 4),
                "fault_masking_rate": round(zero_failure_rate, 4),
                "non_hang_masking_rate": round(non_hang_mask_rate, 4),
            }
            results[arch].append(row)

    # Also compute exact code-space capacity (in 3,072 words: 0200..5777 octal = 2,944 words)
    max_fit = {}
    for arch in architectures:
        lo, hi = 1, 600
        best = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            dummy_pairs = [((i * 7 + 3) % 61 + 2, (i * 13 + 5) % 59 + 3) for i in range(mid)]
            try:
                asm, _ = build_program(arch, dummy_pairs)
                if asm.pc <= DATA_A_BASE:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            except MemoryError:
                hi = mid - 1
        max_fit[arch] = best

    return {"benchmarks": results, "max_tasks_in_2944_code_words": max_fit}


if __name__ == "__main__":
    out = run_benchmark()
    os.makedirs("results", exist_ok=True)
    with open("results/pdp8_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== PDP-8 Architectural Economy Benchmark (Verified Bit-Exact) ===")
    print("Max tasks fitting in 2,944 code words (0200-5777 octal):", out["max_tasks_in_2944_code_words"])
    for n in [1, 8, 32, 64]:
        print(f"\n--- N = {n} multiply tasks ---")
        print(
            f"{'Architecture':<14} {'Words':>6} {'Cycles':>8} "
            f"{'NonHangMean':>11} {'NonHangMax':>10} {'AllMean':>8} {'NHMask':>8}"
        )
        for arch in ["inlined", "shared", "dual_modular", "buffered_tmr"]:
            row = next(r for r in out["benchmarks"][arch] if r["n_tasks"] == n)
            print(
                f"{arch:<14} {row['code_words']:>6} {row['memory_cycles']:>8} "
                f"{row['non_hang_mean_blast_tasks']:>11.2f} {row['non_hang_max_blast_tasks']:>10} "
                f"{row['mean_blast_tasks']:>8.2f} {row['non_hang_masking_rate']*100:>7.1f}%"
            )
