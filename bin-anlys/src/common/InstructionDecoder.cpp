// -*-Mode: C++;-*-

//*BeginPNNLCopyright********************************************************
//
// $HeadURL$
// $Id$
//
//**********************************************************EndPNNLCopyright*

//***************************************************************************
//
// Translate ISA Instructions to MIAMI's "internal representation"
//
//***************************************************************************

//***************************************************************************
// system includes
//***************************************************************************

//***************************************************************************
// MIAMI includes
//***************************************************************************

//***************************************************************************
// DynInst includes
//***************************************************************************

//***************************************************************************
// 
//***************************************************************************

#include "InstructionDecoder.hpp"

#if 0
#include "dyninst-insn-xlate.hpp"
#endif

//***************************************************************************
// 
//***************************************************************************

namespace MIAMI
{

int
InstructionDecoder::decode(unsigned long pc, int len,
			   MIAMI::DecodedInstruction* dInst)
{
  void* pc_ptr = (void*)pc;
  return MIAMI::decode_instruction_at_pc(pc_ptr, len, dInst);
}


int
InstructionDecoder::decode_dbg(unsigned long pc, int len,
			       MIAMI::DecodedInstruction* dInst,
			       const char* ctxt)
{
  using std::cerr;

  std::string ctxt_str = (ctxt) ? ((std::string)ctxt + ":") : "";

  void* pc_ptr = (void*)pc;

  //cerr << "**********************************************************\n"
  //     << ctxt_str << "InstructionDecoder::decode(" << pc_ptr << ")\n\n";

  //MIAMI::dump_instruction_at_pc(pc_ptr, len);
  //std::cout << "\n";

  int ret = MIAMI::decode_instruction_at_pc(pc_ptr, len, dInst);
  if (ret < 0) { } // error while decoding
  
  //DumpInstrList(dInst);
  //cerr << "\n";

  return ret;
}


int
InstructionDecoder::decode_dbg(unsigned long pc, int len,
			       MIAMI::DecodedInstruction* dInst,
			       MIAMI::DecodedInstruction* dInst1,
			       const char* ctxt)
{
  int ret = 0;

#if 0
  if (dInst1) {
    DumpInstrList(dInst1);
  }
#endif

  return ret;
}

} /* namespace MIAMI */


//***************************************************************************
// 
//***************************************************************************

#if 0
int
InstructionDecoder::decode_dyninst(unsigned long pc, int len,
				   MIAMI::DecodedInstruction* dInst,
				   BPatch_function* dyn_func,
				   BPatch_basicBlock* dyn_blk)
{
  void* pc_ptr = (void*)pc;

  int ret = isaXlate_insn(pc_ptr, len, dInst, dyn_func, dyn_blk);
  if (ret < 0) { } // error while decoding
  
  DumpInstrList(dInst);
  cerr << "\n";
  
  return ret;
}
#endif

