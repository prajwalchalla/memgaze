// $Id$
// -*-C++-*-
// * BeginRiceCopyright *****************************************************
// 
// Copyright ((c)) 2002, Rice University 
// All rights reserved.
// 
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
// 
// * Redistributions of source code must retain the above copyright
//   notice, this list of conditions and the following disclaimer.
// 
// * Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in the
//   documentation and/or other materials provided with the distribution.
// 
// * Neither the name of Rice University (RICE) nor the names of its
//   contributors may be used to endorse or promote products derived from
//   this software without specific prior written permission.
// 
// This software is provided by RICE and contributors "as is" and any
// express or implied warranties, including, but not limited to, the
// implied warranties of merchantability and fitness for a particular
// purpose are disclaimed. In no event shall RICE or contributors be
// liable for any direct, indirect, incidental, special, exemplary, or
// consequential damages (including, but not limited to, procurement of
// substitute goods or services; loss of use, data, or profits; or
// business interruption) however caused and on any theory of liability,
// whether in contract, strict liability, or tort (including negligence
// or otherwise) arising in any way out of the use of this software, even
// if advised of the possibility of such damage. 
// 
// ******************************************************* EndRiceCopyright *

//***************************************************************************
//
// File:
//    xml.H
//
// Purpose:
//    Some useful and simple routines for using XML.  The xerces
//    library is much much more complete and powerful, but for simple
//    apps, it can be overkill.
//
// Description:
//    [The set of functions, macros, etc. defined in the file]
//
//***************************************************************************

#ifndef MIAMI_xml_H 
#define MIAMI_xml_H

//************************* System Include Files ****************************

#include <string>
#include <iostream>
#include <sstream>

//*************************** User Include Files ****************************


//*************************** Forward Declarations ***************************

// just like std::get and std::getline, except is not limited by a
// fixed input buffer size
std::string Get(std::istream& is, char end = '\n');
std::string GetLine(std::istream& is, char end = '\n');

// skips the specified string; returns false if there is a
// deviation between 's' and what is read; true otherwise
bool Skip(std::istream& is, const char* s);

//****************************************************************************

namespace xml {
  
  extern const std::string SPC;   // space
  extern const std::string eleB;  // element begin, initial
  extern const std::string eleBf; // element begin, final
  extern const std::string eleE;  // element end, normal
  extern const std::string eleEc; // element end, compact: <.../>
  extern const std::string attB;  // attribute value begin
  extern const std::string attE;  // attribute value end
  
  enum XMLElementI {
    TOKEN = 0,
    ATT1 = 1,
    ATT2 = 2,
    ATT3 = 3,
    ATT4 = 4,
    ATT5 = 5,
    ATT6 = 6,
    ATT7 = 7,
    ATT8 = 8,
    ATT9 = 9
  };

  class RWError { };

  enum {
    ESC_FALSE =	(0 << 0),   /* Do not escape reserved XML chars */
    ESC_TRUE  =	(1 << 0),   /* Escape reserved XML chars */
    UNESC_FALSE = (0 << 0),
    UNESC_TRUE  = (1 << 0)
  }; 

  // Returns the string with all necessary characters (un)escaped; will
  // not modify 'str'
  std::string EscapeStr(const char* str);
  std::string UnEscapeStr(const char* str);  

  // -------------------------------------------------------  
  // Reads from 'attB' to and including 'attE'.  Eats up whitespace
  // before and after the attibute.  
  // -------------------------------------------------------
  bool ReadAttrStr(std::istream& is, std::string& s, int flags = UNESC_TRUE);

  // Read a number into a C/C++ numerical type
  template <class T> bool ReadAttrNum(std::istream& is, T& n)
  {
    bool STATE = true; // false indicates an error
    is >> std::ws;
    STATE &= Skip(is, "=");  is >> std::ws;
    STATE &= Skip(is, "\""); is >> std::ws;
    is >> n;
    STATE &= Skip(is, "\""); is >> std::ws;
    return STATE;
  }
  
  // -------------------------------------------------------  
  // Writes attribute value, beginning with 'attB' and ending with 'attE'
  // -------------------------------------------------------  
  bool WriteAttrStr(std::ostream& os, const char* s, int flags = ESC_TRUE);

  // Write a C/C++ numerical type
  template <class T> bool WriteAttrNum(std::ostream& os, T n)
  {
    os << attB << n << attE;
    return (!os.fail());  
  } 

  // -------------------------------------------------------  
  // Creates an attribute string, beginning with 'attB' and ending with 'attE'
  // -------------------------------------------------------  

  inline std::string MakeAttrStr(const char* s, int flags = ESC_TRUE) {
    std::string str = ((flags & ESC_TRUE) ? EscapeStr(s) : std::string(s));
    return (std::string(attB + str + attE));
  }

  inline std::string MakeAttrNum(int n) {
    std::ostringstream oss;
    oss << attB << n << attE;
    return (oss.str());
  }
  inline std::string MakeAttrNum(unsigned int n, bool hex = false) {
    std::ostringstream oss;
    oss << attB;
    if (hex)
       oss << std::hex << n << std::dec;
    else
       oss << n;
    oss << attE;
    return (oss.str());
  }
  inline std::string MakeAttrNum(long n) {
    std::ostringstream oss;
    oss << attB << n << attE;
    return (oss.str());
  }
  inline std::string MakeAttrNum(unsigned long n, bool hex = false) {
    std::ostringstream oss;
    oss << attB;
    if (hex)
       oss << std::hex << n << std::dec;
    else
       oss << n;
    oss << attE;
    return (oss.str());
  }
 
#ifdef ARCH_USE_LONG_LONG // FIXME:old
  inline std::string MakeAttrNum(long long n) {
    std::ostringstream oss;
    oss << attB << n << attE;
    return (oss.str());
  }
  inline std::string MakeAttrNum(unsigned long long n, bool hex = false) {
    std::ostringstream oss;
    oss << attB;
    if (hex)
       oss << std::hex << n << std::dec;
    else
       oss << n;
    oss << attE;
    return (oss.str());
  }
#endif  
}

#endif
